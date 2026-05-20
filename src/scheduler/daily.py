"""Pipeline giornaliera: genera contenuto e pubblica."""
from __future__ import annotations

import datetime
import tempfile
import uuid

from src.config import Config, load_config
from src.generators.caption import generate_caption
from src.generators.image import generate_image
from src.generators.video import generate_video
from src.publishers.instagram import publish_image
from src.publishers.tiktok import publish_video, TikTokError
from src.storage.r2 import upload_image
from src.storage.history import get_recent_facts, add_to_history


def run_pipeline(cfg: Config | None = None, dry_run: bool = False) -> dict:
    """
    Esegue la pipeline completa:
    1. Genera caption + hashtag via LLM
    2. Genera immagine (Instagram) + video (TikTok)
    3. Carica su R2
    4. Pubblica su Instagram + TikTok (se configurato)

    Se dry_run=True, esegue tutto tranne la pubblicazione finale.
    """
    if cfg is None:
        cfg = load_config()

    results: dict = {}

    print("[1/5] Generazione caption...")
    recent = get_recent_facts(cfg)
    if recent:
        print(f"      Storico: {len(recent)} fatti precedenti caricati da R2.")
    caption_result = generate_caption(cfg, recent_facts=recent)
    results["caption"] = caption_result
    print(f"      Fatto: {caption_result.fact}")

    print("[2/5] Generazione immagine (Instagram)...")
    image_bytes = generate_image(caption_result.fact, caption_result.image_prompt, cfg)
    results["image_bytes"] = len(image_bytes)
    print(f"      Immagine: {len(image_bytes)} bytes")

    print("[3/5] Generazione video (TikTok)...")
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        video_path = tmp.name
    generate_video(caption_result.fact, output_path=video_path)
    print(f"      Video: {video_path}")

    print("[4/5] Upload su R2...")
    date_str = datetime.date.today().isoformat()
    uid = uuid.uuid4().hex[:8]
    img_key = f"posts/{date_str}/{uid}.jpg"
    upload_result = upload_image(cfg, image_bytes, img_key)
    results["image_url"] = upload_result.public_url
    print(f"      Immagine URL: {upload_result.public_url}")

    if dry_run:
        print("[5/5] DRY RUN — pubblicazione saltata.")
        results["published"] = False
        return results

    print("[5/5] Pubblicazione...")

    # Instagram
    print("      [IG] Pubblicazione su Instagram...")
    ig_result = publish_image(cfg, upload_result.public_url, caption_result.full_caption)
    results["ig_media_id"] = ig_result.media_id
    print(f"      [IG] Pubblicato! media_id={ig_result.media_id}")

    # TikTok (opzionale — salta se non configurato)
    if cfg.tiktok_access_token:
        print("      [TT] Pubblicazione su TikTok...")
        try:
            tt_result = publish_video(cfg, video_path, caption_result.full_caption)
            results["tt_publish_id"] = tt_result.publish_id
            print(f"      [TT] Pubblicato! publish_id={tt_result.publish_id}")
        except TikTokError as e:
            print(f"      [TT] ERRORE (Instagram ok): {e}")
            results["tt_error"] = str(e)
    else:
        print("      [TT] Saltato (TIKTOK_ACCESS_TOKEN non configurato)")

    results["published"] = True
    add_to_history(cfg, caption_result.fact, ig_result.media_id)
    print("      Storico aggiornato su R2.")
    if cfg.ig_username:
        print(f"      https://www.instagram.com/{cfg.ig_username}")

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
