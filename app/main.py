from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from app.labels import load_labels
from app.summarizer import render_markdown, summarize_tasks
from app.whatsapp_parser import parse_whatsapp_export


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Podsumowanie zadań z WhatsApp z podziałem na etykiety i kontakty."
    )
    parser.add_argument("export", type=Path, help="Ścieżka do eksportu czatu WhatsApp (txt).")
    parser.add_argument(
        "--labels",
        type=Path,
        help="Ścieżka do pliku YAML z etykietami.",
    )
    parser.add_argument("--model", default="gpt-4o-mini", help="Nazwa modelu OpenAI.")
    parser.add_argument(
        "--language",
        default="pl",
        help="Język odpowiedzi (np. pl).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Plik wynikowy Markdown. Jeśli brak, wynik trafia na stdout.",
    )
    return parser


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()

    messages = parse_whatsapp_export(args.export.read_text(encoding="utf-8").splitlines())
    label_config = load_labels(args.labels)

    grouped_messages: dict[str, list[str]] = defaultdict(list)
    labels_for_contact: dict[str, list[str]] = defaultdict(list)

    for message in messages:
        grouped_messages[message.author].append(message.text)
        labels_for_contact[message.author].extend(
            label_config.labels_for_contact(message.author, message.text)
        )

    label_summary = {
        contact: sorted(set(labels)) for contact, labels in labels_for_contact.items()
    }

    summaries = summarize_tasks(
        grouped_messages=grouped_messages,
        labels=label_summary,
        model=args.model,
        language=args.language,
    )
    markdown = render_markdown(summaries)

    if args.output:
        args.output.write_text(markdown, encoding="utf-8")
    else:
        print(markdown)


if __name__ == "__main__":
    main()
