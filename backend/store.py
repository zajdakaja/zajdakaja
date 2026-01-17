from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List

from backend.models import LabelConfigPayload, TaskCollection, TaskItem


class InMemoryStore:
    def __init__(self) -> None:
        self.labels: Dict[str, LabelConfigPayload] = {}
        self.tasks: Dict[str, TaskCollection] = {}

    def get_labels(self, username: str) -> LabelConfigPayload | None:
        return self.labels.get(username)

    def set_labels(self, username: str, labels: LabelConfigPayload) -> None:
        self.labels[username] = labels

    def get_tasks(self, username: str) -> TaskCollection:
        return self.tasks.get(
            username,
            TaskCollection(tasks=[], updated_at=datetime.now(tz=timezone.utc)),
        )

    def set_tasks(self, username: str, items: List[TaskItem]) -> TaskCollection:
        collection = TaskCollection(tasks=items, updated_at=datetime.now(tz=timezone.utc))
        self.tasks[username] = collection
        return collection


STORE = InMemoryStore()
