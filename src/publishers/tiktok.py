"""Pubblica video su TikTok tramite Content Posting API v2."""
from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import requests

from src.config import Config

API_BASE = "https://open.tiktokapis.com/v2"
CHUNK_SIZE = 10 * 1024 * 1024  # 10 MB per chunk
MAX_POLLS = 20
POLL_INTERVAL = 5


@dataclass
class TikTokPublishResult:
    publish_id: str


class TikTokError(Exception):
    pass


def publish_video(cfg: Config, video_path: str, caption: str) -> TikTokPublishResult:
    """
    Pubblica un video su TikTok tramite Content Posting API v2.
    Richiede TIKTOK_ACCESS_TOKEN e TIKTOK_OPEN_ID nel config.
    """
    if not cfg.tiktok_access_token:
        raise TikTokError("TIKTOK_ACCESS_TOKEN non configurato")
    if not cfg.tiktok_open_id:
        raise TikTokError("TIKTOK_OPEN_ID non configurato")

    video_bytes = Path(video_path).read_bytes()
    video_size = len(video_bytes)

    publish_id, upload_url = _init_upload(cfg, caption, video_size)
    _upload_video(upload_url, video_bytes, video_size)
    _wait_for_publish(cfg, publish_id)

    return TikTokPublishResult(publish_id=publish_id)


def _headers(cfg: Config) -> dict:
    return {
        "Authorization": f"Bearer {cfg.tiktok_access_token}",
        "Content-Type": "application/json; charset=UTF-8",
    }


def _init_upload(cfg: Config, caption: str, video_size: int) -> tuple[str, str]:
    """Inizializza l'upload e ottiene publish_id + upload_url."""
    payload = {
        "post_info": {
            "title": caption[:2200],
            "privacy_level": "PUBLIC_TO_EVERYONE",
            "disable_duet": False,
            "disable_comment": False,
            "disable_stitch": False,
            "ai_generated_content": True,  # required by TikTok policy for AI-generated content
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": video_size,
            "chunk_size": min(CHUNK_SIZE, video_size),
            "total_chunk_count": max(1, -(-video_size // CHUNK_SIZE)),  # ceil division
        },
    }
    r = requests.post(
        f"{API_BASE}/post/publish/video/init/",
        json=payload,
        headers=_headers(cfg),
        timeout=30,
    )
    data = r.json()
    if r.status_code != 200 or data.get("error", {}).get("code") != "ok":
        raise TikTokError(f"Init upload fallito: {r.status_code} {r.text[:300]}")

    publish_id = data["data"]["publish_id"]
    upload_url = data["data"]["upload_url"]
    return publish_id, upload_url


def _upload_video(upload_url: str, video_bytes: bytes, video_size: int) -> None:
    """Carica i chunk video sull'URL fornito da TikTok."""
    chunks = [
        video_bytes[i:i + CHUNK_SIZE]
        for i in range(0, video_size, CHUNK_SIZE)
    ]
    for idx, chunk in enumerate(chunks):
        start = idx * CHUNK_SIZE
        end = start + len(chunk) - 1
        r = requests.put(
            upload_url,
            data=chunk,
            headers={
                "Content-Range": f"bytes {start}-{end}/{video_size}",
                "Content-Type": "video/mp4",
            },
            timeout=120,
        )
        if r.status_code not in (200, 201, 206):
            raise TikTokError(f"Upload chunk {idx} fallito: {r.status_code} {r.text[:200]}")


def _wait_for_publish(cfg: Config, publish_id: str) -> None:
    """Attende che TikTok completi l'elaborazione del video."""
    for i in range(MAX_POLLS):
        time.sleep(POLL_INTERVAL)
        r = requests.post(
            f"{API_BASE}/post/publish/status/fetch/",
            json={"publish_id": publish_id},
            headers=_headers(cfg),
            timeout=15,
        )
        data = r.json()
        status = data.get("data", {}).get("status", "")
        if status == "PUBLISH_COMPLETE":
            return
        if status in ("FAILED", "SPAM_RISK_TOO_MANY_POSTS", "SPAM_RISK_USER_BANNED_FROM_POSTING"):
            raise TikTokError(f"Pubblicazione TikTok fallita: {status}")
    raise TikTokError("Timeout: video TikTok non elaborato dopo polling")
