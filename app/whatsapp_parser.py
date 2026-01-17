from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable


MESSAGE_PATTERN = re.compile(
    r"^(?P<date>\d{1,2}[./]\d{1,2}[./]\d{2,4}),\s*(?P<time>\d{1,2}:\d{2})\s*-\s*(?P<author>[^:]+):\s*(?P<text>.*)$"
)


@dataclass
class WhatsAppMessage:
    timestamp: datetime
    author: str
    text: str


def parse_whatsapp_export(lines: Iterable[str]) -> list[WhatsAppMessage]:
    messages: list[WhatsAppMessage] = []
    current: WhatsAppMessage | None = None

    for raw_line in lines:
        line = raw_line.rstrip("\n")
        match = MESSAGE_PATTERN.match(line)
        if match:
            if current:
                messages.append(current)
            timestamp = _parse_datetime(match.group("date"), match.group("time"))
            current = WhatsAppMessage(
                timestamp=timestamp,
                author=match.group("author").strip(),
                text=match.group("text").strip(),
            )
        elif current:
            current.text += "\n" + line

    if current:
        messages.append(current)

    return [msg for msg in messages if msg.text and "<Media omitted>" not in msg.text]


def _parse_datetime(date_part: str, time_part: str) -> datetime:
    for fmt in ("%d.%m.%Y %H:%M", "%d/%m/%Y %H:%M", "%d.%m.%y %H:%M", "%d/%m/%y %H:%M"):
        try:
            return datetime.strptime(f"{date_part} {time_part}", fmt)
        except ValueError:
            continue
    raise ValueError(f"Nieobsługiwany format daty: {date_part} {time_part}")
