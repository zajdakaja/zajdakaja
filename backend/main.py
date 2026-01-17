from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List

import jwt
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket

from app.labels import LabelConfig, LabelRule, load_labels
from app.summarizer import render_markdown, summarize_tasks
from app.whatsapp_parser import parse_whatsapp_export
from backend.auth import create_access_token, get_current_user, verify_password
from backend.auth import SECRET_KEY, ALGORITHM
from backend.models import (
    LabelConfigPayload,
    LoginRequest,
    SummarizeResponse,
    TaskCollection,
    TaskItem,
    TokenResponse,
    UserProfile,
)
from backend.store import STORE
from backend.websocket_manager import MANAGER

app = FastAPI(title="WhatsApp Task Summarizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(payload: LoginRequest) -> TokenResponse:
    if not verify_password(payload.username, payload.password):
        raise HTTPException(status_code=401, detail="Nieprawidłowe dane logowania")
    token = create_access_token(payload.username)
    return TokenResponse(access_token=token)


@app.get("/api/auth/me", response_model=UserProfile)
async def me(username: str = Depends(get_current_user)) -> UserProfile:
    return UserProfile(username=username)


@app.get("/api/labels", response_model=LabelConfigPayload)
async def get_labels(username: str = Depends(get_current_user)) -> LabelConfigPayload:
    stored = STORE.get_labels(username)
    if stored:
        return stored
    defaults = load_labels(None)
    return LabelConfigPayload(
        labels=[
            {
                "name": rule.name,
                "contacts": list(rule.contacts),
                "keywords": list(rule.keywords),
            }
            for rule in defaults.rules
        ]
    )


@app.post("/api/labels", response_model=LabelConfigPayload)
async def set_labels(
    payload: LabelConfigPayload,
    username: str = Depends(get_current_user),
) -> LabelConfigPayload:
    STORE.set_labels(username, payload)
    await MANAGER.broadcast(username, {"type": "labels", "payload": payload.model_dump()})
    return payload


@app.get("/api/tasks", response_model=TaskCollection)
async def get_tasks(username: str = Depends(get_current_user)) -> TaskCollection:
    return STORE.get_tasks(username)


@app.post("/api/tasks", response_model=TaskCollection)
async def set_tasks(
    items: List[TaskItem],
    username: str = Depends(get_current_user),
) -> TaskCollection:
    collection = STORE.set_tasks(username, items)
    await MANAGER.broadcast(
        username,
        {
            "type": "tasks",
            "payload": collection.model_dump(),
        },
    )
    return collection


@app.post("/api/summarize", response_model=SummarizeResponse)
async def summarize(
    file: UploadFile = File(...),
    username: str = Depends(get_current_user),
) -> SummarizeResponse:
    content = await file.read()
    text = content.decode("utf-8")
    messages = parse_whatsapp_export(text.splitlines())

    stored = STORE.get_labels(username)
    if stored:
        label_config = LabelConfig(
            rules=tuple(
                LabelRule(
                    name=rule.name,
                    contacts=tuple(rule.contacts),
                    keywords=tuple(rule.keywords),
                )
                for rule in stored.labels
            )
        )
    else:
        label_config = load_labels(None)

    grouped: dict[str, list[str]] = {}
    label_summary: dict[str, list[str]] = {}

    for message in messages:
        grouped.setdefault(message.author, []).append(message.text)
        label_summary.setdefault(message.author, [])
        label_summary[message.author].extend(
            label_config.labels_for_contact(message.author, message.text)
        )

    labels = {contact: sorted(set(values)) for contact, values in label_summary.items()}

    summaries = summarize_tasks(
        grouped_messages=grouped,
        labels=labels,
        model="gpt-4o-mini",
        language="pl",
    )
    markdown = render_markdown(summaries)

    tasks: list[TaskItem] = []
    for summary in summaries:
        for task in summary.tasks:
            tasks.append(
                TaskItem(
                    id=str(uuid.uuid4()),
                    category=summary.category,
                    contact=summary.contact,
                    text=task,
                    completed=False,
                )
            )

    STORE.set_tasks(username, tasks)
    await MANAGER.broadcast(
        username,
        {
            "type": "tasks",
            "payload": {
                "tasks": [item.model_dump() for item in tasks],
                "updated_at": datetime.now(tz=timezone.utc).isoformat(),
            },
        },
    )

    return SummarizeResponse(markdown=markdown, tasks=tasks)


@app.websocket("/ws/tasks")
async def tasks_ws(websocket: WebSocket) -> None:
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4401)
        return
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        await websocket.close(code=4401)
        return
    username = decoded.get("sub")
    if not username:
        await websocket.close(code=4401)
        return

    await MANAGER.connect(username, websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        MANAGER.disconnect(username, websocket)
