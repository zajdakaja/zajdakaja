from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Iterable

from openai import OpenAI


@dataclass
class TaskSummary:
    category: str
    contact: str
    tasks: list[str]


SYSTEM_PROMPT = """
Jesteś asystentem do porządkowania zadań z wiadomości WhatsApp.
Zweryfikuj kontekst i zwróć listę zadań do wykonania.
Zawsze odpowiadaj w formacie JSON.
""".strip()


def summarize_tasks(
    grouped_messages: dict[str, list[str]],
    labels: dict[str, list[str]],
    model: str,
    language: str,
) -> list[TaskSummary]:
    client = OpenAI()
    payload = {
        "language": language,
        "labels": labels,
        "messages": grouped_messages,
    }
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Na podstawie danych wejściowych przygotuj listę zadań do wykonania "
                    "w punktach. Podziel zadania na kategorie, które wynikają z etykiet "
                    "użytkownika i nazw kontaktów. Zwróć JSON w formacie: "
                    '{"items":[{"category":"","contact":"","tasks":[""]}]}\n\n'
                    f"Dane: {json.dumps(payload, ensure_ascii=False)}"
                ),
            },
        ],
        temperature=0.2,
    )
    content = response.choices[0].message.content or "{}"
    parsed = json.loads(content)
    summaries: list[TaskSummary] = []
    for item in parsed.get("items", []):
        summaries.append(
            TaskSummary(
                category=item.get("category", "inne"),
                contact=item.get("contact", "nieznany"),
                tasks=list(item.get("tasks", [])),
            )
        )
    return summaries


def render_markdown(summaries: Iterable[TaskSummary]) -> str:
    lines: list[str] = []
    for summary in summaries:
        lines.append(f"## {summary.category} — {summary.contact}")
        for task in summary.tasks:
            lines.append(f"- {task}")
        lines.append("")
    return "\n".join(lines).strip()
