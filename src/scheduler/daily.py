"""Pipeline giornaliera: genera contenuto e pubblica."""
from __future__ import annotations

import datetime
import uuid

from src.config import Config, load_config
from src.generators.caption import generate_caption
from src.generators.image import generate_image
from src.publishers.instagram import publish_image
from src.storage.r2 import upload_image


def run_pipeline(cfg: Config | None = None, dry_run: bool = False) -> dict:
    """
    Esegue la pipeline completa:
    1. Genera caption + hashtag via LLM
    2. Genera immagine
    3. Carica su R2
    4. Pubblica su Instagram

    Se dry_run=True, esegue tutto tranne la pubblicazione finale.
    Ritorna un dict con i risultati di ogni step.
    """
    if cfg is None:
        cfg = load_config()

    results: dict = {}

    print("[1/4] Generazione caption...")
    caption_result = generate_caption(cfg)
    results["caption"] = caption_result
    print(f"      Fatto: {caption_result.fact}")

    print("[2/4] Generazione immagine...")
    image_bytes = generate_image(caption_result.fact, caption_result.image_prompt, cfg)
    results["image_bytes"] = len(image_bytes)
    print(f"      Immagine: {len(image_bytes)} bytes")

    print("[3/4] Upload su R2...")
    date_str = datetime.date.today().isoformat()
    uid = uuid.uuid4().hex[:8]
    key = f"posts/{date_str}/{uid}.jpg"
    upload_result = upload_image(cfg, image_bytes, key)
    results["image_url"] = upload_result.public_url
    print(f"      URL: {upload_result.public_url}")

    if dry_run:
        print("[4/4] DRY RUN — pubblicazione saltata.")
        results["published"] = False
        return results

    print("[4/4] Pubblicazione su Instagram...")
    publish_result = publish_image(cfg, upload_result.public_url, caption_result.full_caption)
    results["media_id"] = publish_result.media_id
    results["published"] = True
    print(f"      Pubblicato! media_id={publish_result.media_id}")
    if cfg.ig_username:
        print(f"      Vai su https://www.instagram.com/{cfg.ig_username}")

    return results


def run_scheduler(cfg: Config | None = None) -> None:
    """Lancia lo scheduler giornaliero (09:00 ogni giorno)."""
    import schedule
    import time

    if cfg is None:
        cfg = load_config()

    def job():
        print(f"\n{'='*50}")
        print(f"Avvio pipeline: {datetime.datetime.now().isoformat()}")
        try:
            run_pipeline(cfg)
        except Exception as e:
            print(f"[ERRORE] Pipeline fallita: {e}")

    schedule.every().day.at("09:00").do(job)
    print("Scheduler avviato. Pipeline ogni giorno alle 09:00. Ctrl+C per uscire.")
    while True:
        schedule.run_pending()
        time.sleep(60)
