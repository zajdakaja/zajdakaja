from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserProfile(BaseModel):
    username: str


class LabelRulePayload(BaseModel):
    name: str
    contacts: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)


class LabelConfigPayload(BaseModel):
    labels: List[LabelRulePayload]


class TaskItem(BaseModel):
    id: str
    category: str
    contact: str
    text: str
    completed: bool = False


class TaskCollection(BaseModel):
    tasks: List[TaskItem]
    updated_at: datetime


class SummarizeResponse(BaseModel):
    markdown: str
    tasks: List[TaskItem]
