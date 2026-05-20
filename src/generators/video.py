"""Genera un video MP4 verticale (1080x1920) con effetto typewriter per TikTok/Reels."""
from __future__ import annotations

import io
import math
import random
import tempfile
import textwrap
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

WIDTH, HEIGHT = 1080, 1920

BG_TOP = (10, 16, 45)
BG_BOTTOM = (3, 6, 20)
ACCENT = (80, 140, 255)
TEXT_PRIMARY = (220, 230, 255)
TEXT_DIM = (140, 170, 220)

# Durata per carattere (secondi)
CHAR_DURATION = 0.06
# Pausa finale a schermo pieno (secondi)
HOLD_DURATION = 3.0
# Frame rate
FPS = 30


def _load_font(path: str, size: int):
    from PIL import ImageFont
    candidates = [
        path,
        path.replace("arialbd.ttf", "DejaVuSans-Bold.ttf"),
        path.replace("arial.ttf", "DejaVuSans.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
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


def _build_base_frame(particles: list[tuple]) -> Image.Image:
    """Costruisce il frame di sfondo (uguale per tutti i frame)."""
    img = Image.new("RGB", (WIDTH, HEIGHT))
    _draw_gradient(img, BG_TOP, BG_BOTTOM)
    d = ImageDraw.Draw(img)

    # Cerchi decorativi
    d.ellipse([(600, -200), (1300, 500)], fill=(18, 32, 78))
    d.ellipse([(640, -160), (1260, 460)], fill=(13, 22, 55))
    d.ellipse([(-250, 1500), (350, 2100)], fill=(16, 30, 72))
    d.ellipse([(-210, 1540), (310, 2060)], fill=(10, 18, 48))

    # Particelle
    for (x, y, r, bright) in particles:
        d.ellipse([(x - r, y - r), (x + r, y + r)], fill=(bright, bright + 20, 255))

    # Punto interrogativo decorativo (sfondo)
    font_deco = _load_font("arialbd.ttf", 600)
    d.text((180, 550), "?", fill=(18, 36, 88), font=font_deco)

    # Barra accent in alto
    d.rectangle([(0, 0), (WIDTH, 8)], fill=ACCENT)

    # Brand name
    font_brand = _load_font("arialbd.ttf", 58)
    d.text((60, 60), "Mr. Curiously", fill=ACCENT, font=font_brand)

    # Label "FATTO DEL GIORNO"
    font_pill = _load_font("arial.ttf", 32)
    d.rounded_rectangle([(60, 145), (400, 196)], radius=16, fill=(28, 55, 115))
    d.text((80, 155), ">> FATTO DEL GIORNO", fill=(160, 200, 255), font=font_pill)

    # Footer
    font_footer = _load_font("arial.ttf", 36)
    d.text((60, HEIGHT - 130), "@mr.curiously", fill=TEXT_DIM, font=font_footer)
    d.text((60, HEIGHT - 80), "Seguici per nuovi fatti ogni giorno!", fill=(80, 110, 170), font=font_footer)
    d.rectangle([(0, HEIGHT - 8), (WIDTH, HEIGHT)], fill=ACCENT)

    return img


def _render_frame(base: Image.Image, text: str, visible_count: int) -> np.ndarray:
    """Renderizza un frame con i primi visible_count caratteri visibili."""
    img = base.copy()
    d = ImageDraw.Draw(img)

    font_fact = _load_font("arialbd.ttf", 62)
    visible_text = text[:visible_count]
    wrapped = textwrap.fill(visible_text, width=20)

    text_y_start = 240
    d.multiline_text((60, text_y_start), wrapped, fill=TEXT_PRIMARY, font=font_fact, spacing=24)

    # Cursore lampeggiante alla fine del testo corrente
    if visible_count < len(text):
        bbox = d.textbbox((60, text_y_start), wrapped, font=font_fact, spacing=24)
        cursor_x = min(bbox[2] + 6, WIDTH - 60)
        cursor_y = bbox[3] - 55
        d.rectangle([(cursor_x, cursor_y), (cursor_x + 5, cursor_y + 52)], fill=ACCENT)

    return np.array(img)


def generate_video(fact: str, output_path: str | None = None) -> str:
    """
    Genera un video MP4 con effetto typewriter lettera per lettera.
    Se output_path e None, salva in un file temporaneo.
    Ritorna il percorso del file MP4 generato.
    """
    from moviepy import ImageSequenceClip

    if output_path is None:
        tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        output_path = tmp.name
        tmp.close()

    rng = random.Random(13)
    particles = [
        (rng.randint(0, WIDTH), rng.randint(0, HEIGHT),
         rng.randint(1, 4), rng.randint(60, 160))
        for _ in range(70)
    ]

    base = _build_base_frame(particles)
    frames = []

    # Fase 1: caratteri appaiono uno alla volta
    for i in range(1, len(fact) + 1):
        frame = _render_frame(base, fact, i)
        n_frames = max(1, int(CHAR_DURATION * FPS))
        frames.extend([frame] * n_frames)

    # Fase 2: testo completo visibile per HOLD_DURATION secondi
    full_frame = _render_frame(base, fact, len(fact))
    frames.extend([full_frame] * int(HOLD_DURATION * FPS))

    clip = ImageSequenceClip(frames, fps=FPS)
    clip.write_videofile(output_path, codec="libx264", audio=False,
                         ffmpeg_params=["-crf", "23", "-preset", "fast"],
                         logger=None)
    clip.close()

    return output_path
