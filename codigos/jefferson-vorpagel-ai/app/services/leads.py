import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def save_record(file_path: Path, payload: dict[str, Any]) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)

    record = {"created_at": datetime.now(timezone.utc).isoformat()}
    for key, value in payload.items():
        record[key] = value.strip() if isinstance(value, str) else value

    if isinstance(record.get("email"), str):
        record["email"] = record["email"].lower()

    with file_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")


def save_lead(leads_file: Path, payload: dict[str, Any]) -> None:
    save_record(leads_file, payload)
