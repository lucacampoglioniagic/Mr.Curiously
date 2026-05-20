"""CLI per Mr. Curiously — comandi manuali."""
import click

from src.config import load_config


@click.group()
def cli():
    """Mr. Curiously — Auto Content Publisher."""
    pass


@cli.command("run")
def cmd_run():
    """Esegue la pipeline completa (genera + pubblica)."""
    from src.scheduler.daily import run_pipeline

    cfg = load_config()
    run_pipeline(cfg, dry_run=False)


@cli.command("dry-run")
def cmd_dry_run():
    """Esegue la pipeline senza pubblicare (test completo)."""
    from src.scheduler.daily import run_pipeline

    cfg = load_config()
    run_pipeline(cfg, dry_run=True)


@cli.command("test-instagram")
def cmd_test_instagram():
    """Verifica la connessione a Instagram con un'immagine di test."""
    import io
    import uuid

    import requests
    from PIL import Image, ImageDraw, ImageFont

    from src.storage.r2 import upload_image
    from src.publishers.instagram import publish_image

    cfg = load_config()
    click.echo("Generazione immagine di test...")

    img = Image.new("RGB", (1080, 1080), (15, 20, 40))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arialbd.ttf", 72)
    except Exception:
        font = ImageFont.load_default()
    d.text((110, 460), "Mr. Curiously", fill=(80, 140, 255), font=font)
    d.text((110, 570), "Test post ✓", fill=(220, 230, 255), font=font)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    image_bytes = buf.getvalue()

    click.echo(f"Immagine: {len(image_bytes)} bytes")
    key = f"test/{uuid.uuid4().hex[:8]}-test.jpg"
    upload_result = upload_image(cfg, image_bytes, key)
    click.echo(f"URL: {upload_result.public_url}")

    # Verifica che l'URL sia raggiungibile
    r = requests.get(upload_result.public_url, timeout=15)
    click.echo(f"Verifica URL: HTTP {r.status_code}")
    if r.status_code != 200:
        raise click.ClickException("URL pubblico non raggiungibile!")

    click.echo("Pubblicazione su Instagram...")
    result = publish_image(cfg, upload_result.public_url, "Test automatico 🧠\n\n#mrcuriously #test")
    click.echo(click.style(f"✓ Pubblicato! media_id={result.media_id}", fg="green"))
    if cfg.ig_username:
        click.echo(f"Vai su https://www.instagram.com/{cfg.ig_username}")


@cli.command("profile-image")
@click.option("--output", default="profile.png", help="Percorso file output (default: profile.png)")
@click.option("--upload", is_flag=True, help="Carica anche su R2")
def cmd_profile_image(output: str, upload: bool):
    """Genera l'immagine profilo Instagram e la salva in locale."""
    from src.generators.profile import generate_profile_image

    click.echo("Generazione immagine profilo...")
    image_bytes = generate_profile_image()
    with open(output, "wb") as f:
        f.write(image_bytes)
    click.echo(click.style(f"Salvata: {output} ({len(image_bytes):,} bytes)", fg="green"))

    if upload:
        from src.storage.r2 import upload_image
        cfg = load_config()
        result = upload_image(cfg, image_bytes, "profile/profile.png", content_type="image/png")
        click.echo(f"Caricata su R2: {result.public_url}")

    click.echo("Carica manualmente su Instagram: Impostazioni → Modifica profilo → Foto profilo")


@cli.command("test-video")
@click.option("--fact", default=None, help="Fatto da animare (default: usa mock)")
@click.option("--output", default="test_video.mp4", help="File output (default: test_video.mp4)")
def cmd_test_video(fact: str | None, output: str):
    """Genera un video TikTok di test con effetto typewriter."""
    from src.generators.video import generate_video
    from src.generators.caption import _mock_caption

    if not fact:
        result = _mock_caption([])
        fact = result.fact

    click.echo(f"Generazione video per: {fact[:60]}...")
    path = generate_video(fact, output_path=output)
    click.echo(click.style(f"Video salvato: {path}", fg="green"))


@cli.command("test-tiktok")
def cmd_test_tiktok():
    """Genera un video di test e lo pubblica su TikTok."""
    from src.generators.video import generate_video
    from src.generators.caption import _mock_caption
    from src.publishers.tiktok import publish_video
    import tempfile

    cfg = load_config()
    caption_result = _mock_caption([])

    click.echo(f"Fatto: {caption_result.fact[:60]}...")
    click.echo("Generazione video...")
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        video_path = tmp.name
    generate_video(caption_result.fact, output_path=video_path)
    click.echo(f"Video: {video_path}")

    click.echo("Pubblicazione su TikTok...")
    result = publish_video(cfg, video_path, caption_result.full_caption)
    click.echo(click.style(f"Pubblicato! publish_id={result.publish_id}", fg="green"))


@cli.command("schedule")
def cmd_schedule():
    """Avvia lo scheduler giornaliero (09:00 ogni giorno)."""
    from src.scheduler.daily import run_scheduler

    run_scheduler()


if __name__ == "__main__":
    cli()
