from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml


@dataclass(frozen=True)
class LabelRule:
    name: str
    contacts: tuple[str, ...]
    keywords: tuple[str, ...]


@dataclass(frozen=True)
class LabelConfig:
    rules: tuple[LabelRule, ...]

    def labels_for_contact(self, contact: str, message: str) -> list[str]:
        hits: list[str] = []
        lowered = message.lower()
        for rule in self.rules:
            if contact in rule.contacts:
                hits.append(rule.name)
                continue
            if any(keyword in lowered for keyword in rule.keywords):
                hits.append(rule.name)
        return hits


DEFAULT_LABELS = LabelConfig(
    rules=(
        LabelRule(name="dom", contacts=(), keywords=("rachunki", "naprawa", "zakupy")),
        LabelRule(name="firma", contacts=(), keywords=("projekt", "faktura", "umowa")),
        LabelRule(name="towarzyskie", contacts=(), keywords=("spotkanie", "kawa", "kino")),
    )
)


def load_labels(path: Path | None) -> LabelConfig:
    if not path:
        return DEFAULT_LABELS
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rules_data: Iterable[dict] = data.get("labels", [])
    rules = []
    for entry in rules_data:
        rules.append(
            LabelRule(
                name=str(entry.get("name")),
                contacts=tuple(entry.get("contacts", [])),
                keywords=tuple(entry.get("keywords", [])),
            )
        )
    return LabelConfig(rules=tuple(rules))
