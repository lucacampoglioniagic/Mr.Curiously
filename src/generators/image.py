"""Genera l'immagine 1080x1080 per il post."""
from __future__ import annotations

import io
import textwrap

from PIL import Image, ImageDraw, ImageFont

from src.config import Config

# Palette colori di Mr. Curiously
BG_COLOR = (15, 20, 40)
ACCENT_COLOR = (80, 140, 255)
TEXT_PRIMARY = (220, 230, 255)
TEXT_SECONDARY = (140, 170, 220)
SIZE = (1080, 1080)


def _load_font(path: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    # Fallback chain: font richiesto → equivalenti Linux → default
    candidates = [
        path,
        path.replace("arialbd.ttf", "DejaVuSans-Bold.ttf"),
        path.replace("arial.ttf", "DejaVuSans.ttf"),
        path.replace("arialbd.ttf", "LiberationSans-Bold.ttf"),
        path.replace("arial.ttf", "LiberationSans-Regular.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            continue
    return ImageFont.load_default(size=size) if hasattr(ImageFont, "load_default") else ImageFont.load_default()


def generate_image(fact: str, image_prompt: str = "", cfg: Config | None = None) -> bytes:
    """
    Genera un'immagine JPEG 1080x1080.
    Se OPENAI_API_KEY è disponibile e image_prompt non è vuoto, usa DALL-E 3.
    Altrimenti genera un'immagine branded con Pillow.
    """
    if cfg and cfg.openai_api_key and image_prompt:
        try:
            return _generate_dalle(cfg, image_prompt)
        except Exception as e:
            print(f"[image] DALL-E fallito ({e}), uso Pillow fallback")

    return _generate_pillow(fact)


def _generate_dalle(cfg: Config, image_prompt: str) -> bytes:
    from openai import OpenAI
    import requests

    client = OpenAI(api_key=cfg.openai_api_key)
    response = client.images.generate(
        model="dall-e-3",
        prompt=f"Digital illustration, clean minimal style, dark blue background. {image_prompt}",
        size="1024x1024",
        quality="standard",
        n=1,
    )
    url = response.data[0].url
    r = requests.get(url, timeout=30)
    r.raise_for_status()

    # Ridimensiona a 1080x1080
    img = Image.open(io.BytesIO(r.content)).resize(SIZE, Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92, optimize=True)
    return buf.getvalue()


def _draw_gradient(img: Image.Image, top: tuple, bottom: tuple) -> None:
    """Disegna un gradiente verticale sull'immagine."""
    d = ImageDraw.Draw(img)
    for y in range(img.height):
        t = y / img.height
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        d.line([(0, y), (img.width, y)], fill=(r, g, b))


def _generate_pillow(fact: str) -> bytes:
    import random
    img = Image.new("RGB", SIZE)

    # Sfondo gradiente
    _draw_gradient(img, (10, 16, 45), (5, 8, 28))
    d = ImageDraw.Draw(img)

    # Cerchi decorativi di sfondo
    d.ellipse([(700, -120), (1200, 380)], fill=(20, 40, 90))
    d.ellipse([(730, -90), (1170, 350)], fill=(15, 28, 65))
    d.ellipse([(-180, 750), (280, 1210)], fill=(18, 35, 80))
    d.ellipse([(-150, 780), (250, 1180)], fill=(12, 22, 55))

    # Particelle/stelle di sfondo
    rng = random.Random(42)
    for _ in range(60):
        x, y = rng.randint(0, 1080), rng.randint(0, 1080)
        r = rng.randint(1, 3)
        alpha = rng.randint(60, 160)
        d.ellipse([(x - r, y - r), (x + r, y + r)], fill=(alpha, alpha + 20, 255))

    # Punto interrogativo grande decorativo (sfondo)
    font_deco = _load_font("arialbd.ttf", 420)
    d.text((570, 190), "?", fill=(22, 45, 100), font=font_deco)

    # Barra accent in alto
    d.rectangle([(0, 0), (1080, 6)], fill=ACCENT_COLOR)

    # Brand
    font_brand = _load_font("arialbd.ttf", 46)
    d.text((60, 55), "Mr. Curiously", fill=ACCENT_COLOR, font=font_brand)

    # Label "FATTO DEL GIORNO"
    d.rounded_rectangle([(60, 118), (338, 160)], radius=14, fill=(30, 60, 120))
    font_pill = _load_font("arial.ttf", 26)
    d.text((78, 128), ">> FATTO DEL GIORNO", fill=(160, 200, 255), font=font_pill)

    # Fatto curioso principale
    font_fact = _load_font("arialbd.ttf", 52)
    wrapped = textwrap.fill(fact, width=26)
    d.multiline_text((60, 210), wrapped, fill=TEXT_PRIMARY, font=font_fact, spacing=20)

    # Linea separatore
    d.rectangle([(60, 840), (400, 843)], fill=ACCENT_COLOR)

    # Footer
    font_footer = _load_font("arial.ttf", 32)
    d.text((60, 860), "@mr.curiously", fill=TEXT_SECONDARY, font=font_footer)
    d.text((60, 910), "Seguici per nuovi fatti ogni giorno!", fill=(100, 130, 180), font=font_footer)

    # Barra accent in basso
    d.rectangle([(0, 1074), (1080, 1080)], fill=ACCENT_COLOR)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92, optimize=True)
    return buf.getvalue()
