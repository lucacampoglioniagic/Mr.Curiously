"""Genera l'immagine profilo Instagram per Mr. Curiously (1080x1080, crop circolare)."""
from __future__ import annotations

import io
import math

from PIL import Image, ImageDraw

SIZE = 1080
BG_TOP = (10, 16, 45)
BG_BOTTOM = (5, 8, 28)
ACCENT = (80, 140, 255)
TEXT_PRIMARY = (220, 230, 255)
TEXT_DIM = (140, 170, 220)


def _load_font(path: str, size: int):
    from PIL import ImageFont
    candidates = [
        path,
        path.replace("arialbd.ttf", "DejaVuSans-Bold.ttf"),
        path.replace("arial.ttf", "DejaVuSans.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for c in candidates:
        try:
            return ImageFont.truetype(c, size)
        except Exception:
            continue
    return ImageFont.load_default(size=size) if hasattr(ImageFont, "load_default") else ImageFont.load_default()


def _draw_gradient(img: Image.Image, top: tuple, bottom: tuple) -> None:
    d = ImageDraw.Draw(img)
    for y in range(img.height):
        t = y / img.height
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        d.line([(0, y), (img.width, y)], fill=(r, g, b))


def generate_profile_image() -> bytes:
    """
    Genera un'immagine profilo Instagram 1080x1080.
    Design: cerchio con punto interrogativo centrale, brand name, tagline.
    Instagram croppera l'immagine in un cerchio, quindi il design e centrato.
    """
    import random
    img = Image.new("RGB", (SIZE, SIZE))
    _draw_gradient(img, BG_TOP, BG_BOTTOM)
    d = ImageDraw.Draw(img)

    cx, cy = SIZE // 2, SIZE // 2

    # Cerchio esterno (bordo glow)
    r_outer = 480
    d.ellipse([(cx - r_outer, cy - r_outer), (cx + r_outer, cy + r_outer)], fill=(18, 32, 80))

    # Anello accent
    r_ring = 460
    for thickness in range(8, 0, -1):
        alpha = int(255 * (thickness / 8) * 0.6)
        d.ellipse(
            [(cx - r_ring - thickness, cy - r_ring - thickness),
             (cx + r_ring + thickness, cy + r_ring + thickness)],
            outline=(*ACCENT, alpha) if len(ACCENT) == 3 else ACCENT,
            width=1,
        )
    d.ellipse([(cx - r_ring, cy - r_ring), (cx + r_ring, cy + r_ring)], outline=ACCENT, width=4)

    # Particelle
    rng = random.Random(7)
    for _ in range(40):
        angle = rng.uniform(0, 2 * math.pi)
        dist = rng.uniform(200, 430)
        x = int(cx + dist * math.cos(angle))
        y = int(cy + dist * math.sin(angle))
        r = rng.randint(2, 5)
        bright = rng.randint(80, 180)
        d.ellipse([(x - r, y - r), (x + r, y + r)], fill=(bright, bright + 20, 255))

    # Punto interrogativo grande centrale
    font_q = _load_font("arialbd.ttf", 420)
    q_text = "?"
    bbox = d.textbbox((0, 0), q_text, font=font_q)
    qw, qh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text((cx - qw // 2, cy - qh // 2 - 60), q_text, fill=ACCENT, font=font_q)

    # Brand name
    font_brand = _load_font("arialbd.ttf", 68)
    brand = "Mr. Curiously"
    bbox = d.textbbox((0, 0), brand, font=font_brand)
    bw = bbox[2] - bbox[0]
    d.text((cx - bw // 2, cy + 310), brand, fill=TEXT_PRIMARY, font=font_brand)

    # Tagline
    font_tag = _load_font("arial.ttf", 34)
    tagline = "Fatti curiosi ogni giorno"
    bbox = d.textbbox((0, 0), tagline, font=font_tag)
    tw = bbox[2] - bbox[0]
    d.text((cx - tw // 2, cy + 396), tagline, fill=TEXT_DIM, font=font_tag)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
