"""Genera fatto curioso + caption + hashtag via LLM (OpenAI o Anthropic)."""
from __future__ import annotations

import json
from dataclasses import dataclass

from src.config import Config

SYSTEM_PROMPT = """Sei Mr. Curiously, un account Instagram divulgativo e curioso.
Genera UN fatto curioso, interessante e verificabile su qualsiasi argomento (scienza, storia, natura, spazio, ecc.).
Rispondi SOLO con un JSON valido, nessun testo extra, con questa struttura:
{
  "fact": "il fatto curioso in una frase breve e accattivante",
  "caption": "caption Instagram completa (2-4 righe, emoji, tono coinvolgente), il fatto come primo paragrafo, seguita da domanda al lettore",
  "hashtags": ["tag1", "tag2", ...],
  "image_prompt": "descrizione per generare un'immagine evocativa del fatto (in inglese, stile illustrazione digitale)"
}
Lingua: italiano per fact/caption, inglese per image_prompt."""


@dataclass
class CaptionResult:
    fact: str
    caption: str
    hashtags: list[str]
    image_prompt: str

    @property
    def full_caption(self) -> str:
        tags = " ".join(f"#{t.lstrip('#')}" for t in self.hashtags)
        return f"{self.caption}\n\n{tags}"


def generate_caption(cfg: Config, mock: bool = False) -> CaptionResult:
    """Genera caption usando OpenAI (preferito) o Anthropic come fallback.
    Se mock=True o nessuna API key è configurata, restituisce dati di test."""
    if mock or (not cfg.openai_api_key and not cfg.anthropic_api_key):
        if not mock:
            print("      [AVVISO] Nessuna API key AI — uso caption di test.")
        return _mock_caption()
    if cfg.openai_api_key:
        return _generate_openai(cfg)
    return _generate_anthropic(cfg)


def _mock_caption() -> CaptionResult:
    return CaptionResult(
        fact="Gli squali esistono da prima degli alberi: comparvero 450 milioni di anni fa, mentre le foreste apparvero solo 350 milioni di anni fa.",
        caption="Gli squali sono piu' antichi degli alberi.\n\nQuando i primi squali nuotavano negli oceani, sulla Terra non esisteva ancora nessuna foresta. Le piante non avevano ancora colonizzato la terraferma.\n450 milioni di anni di evoluzione quasi perfetta: nessun predatore marino ha mai eguagliato questo record.\n\nQuale fatto sulla preistoria ti ha sempre stupito di piu'?",
        hashtags=["squali", "preistoria", "evoluzione", "scienza", "natura", "mrcuriously", "fatticuriosi", "oceano"],
        image_prompt="Ancient prehistoric shark swimming in a primordial ocean, no trees visible on distant shores, dramatic lighting, digital illustration",
    )


def _parse_response(text: str) -> CaptionResult:
    # Estrae il JSON anche se il modello aggiunge testo prima/dopo
    start = text.find("{")
    end = text.rfind("}") + 1
    data = json.loads(text[start:end])
    return CaptionResult(
        fact=data["fact"],
        caption=data["caption"],
        hashtags=data.get("hashtags", []),
        image_prompt=data.get("image_prompt", ""),
    )


def _generate_openai(cfg: Config) -> CaptionResult:
    from openai import OpenAI

    client = OpenAI(api_key=cfg.openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Genera un fatto curioso."},
        ],
        temperature=0.9,
        max_tokens=600,
    )
    return _parse_response(response.choices[0].message.content)


def _generate_anthropic(cfg: Config) -> CaptionResult:
    import anthropic

    client = anthropic.Anthropic(api_key=cfg.anthropic_api_key)
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=600,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": "Genera un fatto curioso."}],
    )
    return _parse_response(message.content[0].text)
