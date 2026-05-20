"""Pubblica contenuti su Instagram tramite Graph API."""
from __future__ import annotations

import time
from dataclasses import dataclass

import requests

from src.config import Config

GRAPH = "https://graph.instagram.com/v21.0"
POLL_INTERVAL = 3
MAX_POLLS = 20


@dataclass
class PublishResult:
    media_id: str
    permalink: str | None = None


class InstagramError(Exception):
    pass


def publish_image(cfg: Config, image_url: str, caption: str) -> PublishResult:
    """
    Crea un container media e pubblica il post su Instagram.
    Ritorna il media_id del post pubblicato.
    """
    container_id = _create_container(cfg, image_url, caption)
    _wait_for_ready(cfg, container_id)
    media_id = _publish_container(cfg, container_id)
    return PublishResult(media_id=media_id)


def _create_container(cfg: Config, image_url: str, caption: str) -> str:
    r = requests.post(
        f"{GRAPH}/{cfg.ig_user_id}/media",
        data={
            "image_url": image_url,
            "caption": caption,
            "access_token": cfg.ig_access_token,
        },
        timeout=30,
    )
    if r.status_code != 200:
        raise InstagramError(f"Creazione container fallita: {r.status_code} {r.text[:300]}")
    return r.json()["id"]


def _wait_for_ready(cfg: Config, container_id: str) -> None:
    for i in range(MAX_POLLS):
        time.sleep(POLL_INTERVAL)
        r = requests.get(
            f"{GRAPH}/{container_id}",
            params={"fields": "status_code", "access_token": cfg.ig_access_token},
            timeout=15,
        )
        status = r.json().get("status_code", "")
        if status == "FINISHED":
            return
        if status == "ERROR":
            raise InstagramError(f"Elaborazione media fallita (poll {i})")
    raise InstagramError("Timeout: media non pronto dopo polling")


def _publish_container(cfg: Config, container_id: str) -> str:
    r = requests.post(
        f"{GRAPH}/{cfg.ig_user_id}/media_publish",
        data={
            "creation_id": container_id,
            "access_token": cfg.ig_access_token,
        },
        timeout=30,
    )
    if r.status_code != 200:
        raise InstagramError(f"Pubblicazione fallita: {r.status_code} {r.text[:300]}")
    return r.json()["id"]
