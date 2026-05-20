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



def cmd_schedule():
    """Avvia lo scheduler giornaliero (09:00 ogni giorno)."""
    from src.scheduler.daily import run_scheduler

    run_scheduler()


if __name__ == "__main__":
    cli()
