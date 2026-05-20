"""Gestione storico pubblicazioni su R2 (history/published.json)."""
from __future__ import annotations

import json
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.config import Config

HISTORY_KEY = "history/published.json"
MAX_HISTORY = 60  # ultimi N fatti tenuti in memoria


def load_history(cfg: "Config") -> list[dict]:
    """Carica lo storico da R2. Ritorna lista vuota se non esiste."""
    from src.storage.r2 import get_client

    client = get_client(cfg)
    try:
        response = client.get_object(Bucket=cfg.r2_bucket, Key=HISTORY_KEY)
        return json.loads(response["Body"].read())
    except client.exceptions.NoSuchKey:
        return []
    except Exception:
        return []


def save_history(cfg: "Config", history: list[dict]) -> None:
    """Salva lo storico su R2."""
    from src.storage.r2 import get_client

    client = get_client(cfg)
    data = json.dumps(history[-MAX_HISTORY:], ensure_ascii=False, indent=2)
    client.put_object(
        Bucket=cfg.r2_bucket,
        Key=HISTORY_KEY,
        Body=data.encode("utf-8"),
        ContentType="application/json",
    )


def add_to_history(cfg: "Config", fact: str, media_id: str) -> None:
    """Aggiunge un fatto allo storico e salva su R2."""
    history = load_history(cfg)
    history.append({
        "date": date.today().isoformat(),
        "fact": fact,
        "media_id": media_id,
    })
    save_history(cfg, history)


def get_recent_facts(cfg: "Config", n: int = 20) -> list[str]:
    """Ritorna gli ultimi N fatti pubblicati (per evitare ripetizioni)."""
    history = load_history(cfg)
    return [entry["fact"] for entry in history[-n:]]
