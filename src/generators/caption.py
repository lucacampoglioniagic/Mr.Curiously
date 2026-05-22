"""Genera fatto curioso + caption + hashtag via LLM (OpenAI o Anthropic)."""
from __future__ import annotations

import json
import random
from dataclasses import dataclass

from src.config import Config

SYSTEM_PROMPT = """Sei Mr. Curiously, un account Instagram divulgativo e curioso.
Genera UN fatto curioso, interessante e verificabile su qualsiasi argomento (scienza, storia, natura, spazio, ecc.).
Rispondi SOLO con un JSON valido, nessun testo extra, con questa struttura:
{
  "fact": "il fatto curioso in una frase breve e accattivante",
  "caption": "caption Instagram completa (2-4 righe, tono coinvolgente), il fatto come primo paragrafo, seguita da domanda al lettore",
  "hashtags": ["tag1", "tag2", ...],
  "image_prompt": "descrizione per generare un immagine evocativa del fatto (in inglese, stile illustrazione digitale)"
}
Lingua: italiano per fact/caption, inglese per image_prompt."""

MOCK_FACTS = [
    {
        "fact": "Gli squali esistono da prima degli alberi: comparvero 450 milioni di anni fa, le foreste solo 350 milioni di anni fa.",
        "caption": "Gli squali sono piu antichi degli alberi.\n\nQuando i primi squali nuotavano negli oceani, sulla Terra non esisteva ancora nessuna foresta.\n450 milioni di anni di evoluzione quasi perfetta.\n\nQuale fatto sulla preistoria ti ha sempre stupito?",
        "hashtags": ["squali", "preistoria", "evoluzione", "scienza", "natura", "mrcuriously", "fatticuriosi"],
        "image_prompt": "Ancient prehistoric shark in primordial ocean, no trees on distant shores, dramatic lighting, digital illustration",
    },
    {
        "fact": "Il miele non scade mai: in tombe egizie sono stati trovati vasi di miele commestibile dopo 3.000 anni.",
        "caption": "Il miele e immortale.\n\nIn tombe egizie oltre 3.000 anni fa, gli archeologi hanno trovato miele ancora perfettamente commestibile.\nIl basso contenuto d acqua e il pH acido rendono impossibile la crescita batterica.\n\nSai qual e l alimento piu antico che hai in casa?",
        "hashtags": ["miele", "egitto", "scienza", "alimentazione", "mrcuriously", "fatticuriosi", "storia"],
        "image_prompt": "Ancient Egyptian golden honey jar surrounded by hieroglyphs, warm golden light, digital illustration",
    },
    {
        "fact": "I polpi hanno tre cuori: due pompano sangue verso le branchie, uno verso il corpo. Il loro sangue e blu.",
        "caption": "I polpi hanno tre cuori e sangue blu.\n\nDue cuori pompano il sangue verso le branchie, il terzo lo distribuisce al corpo.\nIl blu e dovuto all emocianina, una molecola che usa il rame al posto del ferro.\n\nQuale animale marino ti affascina di piu?",
        "hashtags": ["polpi", "oceano", "biologia", "scienza", "natura", "mrcuriously", "fatticuriosi"],
        "image_prompt": "Majestic octopus in deep blue ocean, bioluminescent glow, digital illustration",
    },
    {
        "fact": "Oxford University e piu antica degli Aztechi: prime lezioni nel 1096, impero azteco fondato nel 1428.",
        "caption": "Oxford e piu antica degli Aztechi.\n\nQuando gli Aztechi fondarono il loro impero nel 1428, Oxford aveva gia oltre 300 anni di storia.\nLe prime lezioni risalgono al 1096.\n\nCosa ti sembra impossibile ma e reale?",
        "hashtags": ["storia", "oxford", "aztechi", "curiosita", "universita", "mrcuriously", "fatticuriosi"],
        "image_prompt": "Oxford university ancient building next to Aztec pyramid, surreal juxtaposition, digital illustration",
    },
    {
        "fact": "Un giorno su Venere e piu lungo di un anno su Venere: 243 giorni per ruotare, solo 225 per orbitare il Sole.",
        "caption": "Su Venere il giorno e piu lungo dell anno.\n\nVenere impiega 243 giorni terrestri per ruotare su se stesso, ma solo 225 per fare il giro del Sole.\nE gira al contrario rispetto alla Terra.\n\nQuale fatto sullo spazio ti lascia senza parole?",
        "hashtags": ["venere", "spazio", "astronomia", "pianeti", "scienza", "mrcuriously", "fatticuriosi"],
        "image_prompt": "Planet Venus with dramatic orange clouds, surreal day-night cycle, digital illustration",
    },
    {
        "fact": "I fenicotteri sono rosa perche mangiano gamberi. Senza quella dieta, diventerebbero bianchi.",
        "caption": "I fenicotteri non nascono rosa.\n\nIl colore iconico dipende completamente dalla dieta: i carotenoidi nei gamberi si accumulano nelle piume.\nIn cattivita senza la giusta alimentazione, diventano bianchi.\n\nQuale animale nasconde un segreto a sorpresa?",
        "hashtags": ["fenicotteri", "natura", "biologia", "animali", "curiosita", "mrcuriously", "fatticuriosi"],
        "image_prompt": "Flamingo flock in pink lake at sunset, vibrant colors, digital illustration",
    },
    {
        "fact": "Il cuore di una balena blu e grande come un auto e batte solo 2 volte al minuto durante le immersioni.",
        "caption": "Il cuore di una balena blu e grande come un auto.\n\nPesa circa 180 kg e durante le immersioni batte appena 2 volte al minuto.\nI vasi sanguigni sono cosi larghi che un essere umano potrebbe nuotarci dentro.\n\nQuale record animale ti stupisce di piu?",
        "hashtags": ["balena", "oceano", "biologia", "natura", "record", "mrcuriously", "fatticuriosi"],
        "image_prompt": "Blue whale giant heart underwater visualization, deep ocean blue light, anatomical illustration",
    },
    {
        "fact": "Il cielo di Marte al tramonto e blu, al contrario della Terra dove il tramonto e arancione.",
        "caption": "Su Marte i tramonti sono blu.\n\nSulla Terra il cielo e blu di giorno e arancione al tramonto. Su Marte e esattamente il contrario.\nTutto dipende dalla dimensione delle particelle di polvere nell atmosfera.\n\nTi piacerebbe vedere un tramonto marziano?",
        "hashtags": ["marte", "spazio", "astronomia", "nasa", "curiosita", "mrcuriously", "fatticuriosi"],
        "image_prompt": "Mars sunset with blue sky gradient, red dusty landscape, alien planet, digital illustration",
    },
    {
        "fact": "Gli alberi comunicano tra loro attraverso una rete di funghi sotterranea chiamata Wood Wide Web.",
        "caption": "Le foreste hanno un loro internet sotterraneo.\n\nGli alberi si scambiano nutrienti e segnali di pericolo attraverso una rete di funghi chiamata micorriza.\nGli alberi piu grandi nutrono i piu piccoli.\n\nTi cambia il modo in cui guardi un bosco?",
        "hashtags": ["natura", "alberi", "foresta", "biologia", "scienza", "mrcuriously", "fatticuriosi"],
        "image_prompt": "Underground forest network glowing roots and fungi connections, bioluminescent blue light, cross section view, digital illustration",
    },
    {
        "fact": "La Torre Eiffel e piu alta d estate: il calore dilata il ferro di circa 15 cm.",
        "caption": "La Torre Eiffel cresce d estate.\n\nIn estate con temperature alte, la Torre Eiffel e circa 15 cm piu alta rispetto all inverno.\nE lo stesso principio per cui i binari ferroviari hanno piccoli spazi tra i pezzi.\n\nQuale fatto di fisica quotidiana ti sorprende di piu?",
        "hashtags": ["fisica", "torreeiffel", "parigi", "scienza", "curiosita", "mrcuriously", "fatticuriosi"],
        "image_prompt": "Eiffel Tower summer vs winter size comparison, thermal expansion visualization, digital illustration",
    },
    {
        "fact": "Un fulmine e cinque volte piu caldo della superficie del Sole: raggiunge circa 30.000 Kelvin.",
        "caption": "Un fulmine e piu caldo del Sole.\n\nLa superficie del Sole e a circa 5.500 gradi Celsius. Un fulmine raggiunge 30.000 Kelvin, cinque volte di piu.\nTutto in una frazione di secondo.\n\nQuale fenomeno atmosferico ti affascina di piu?",
        "hashtags": ["fulmine", "fisica", "sole", "meteo", "scienza", "mrcuriously", "fatticuriosi"],
        "image_prompt": "Lightning bolt striking at night, electric blue white plasma discharge, dramatic dark sky, digital illustration",
    },
    {
        "fact": "Esistono piu stelle nell universo osservabile che granelli di sabbia su tutte le spiagge e deserti della Terra.",
        "caption": "Le stelle sono piu numerose dei granelli di sabbia.\n\nSi stima ci siano circa 10^24 stelle nell universo osservabile.\nI granelli di sabbia sulla Terra sono circa 7.5 x 10^18. Le stelle vincono per mille volte.\n\nCosa ti fa sentire piu piccolo?",
        "hashtags": ["spazio", "universo", "stelle", "astronomia", "scienza", "mrcuriously", "fatticuriosi"],
        "image_prompt": "Infinite starfield universe compared to sandy beach, deep space photography style, digital illustration",
    },
    {
        "fact": "Il ghiaccio galleggia perche l acqua si espande congelando: senza questa proprieta i laghi ghiaccierebbero dal fondo.",
        "caption": "Il ghiaccio galleggiante ha salvato la vita sulla Terra.\n\nQuasi tutte le sostanze si contraggono congelando. L acqua no: si espande.\nQuesto fa galleggiare il ghiaccio, che isola il lago come una coperta e protegge la vita sotto.\n\nQuale proprieta dell acqua ti sembra piu straordinaria?",
        "hashtags": ["acqua", "fisica", "scienza", "natura", "vita", "mrcuriously", "fatticuriosi"],
        "image_prompt": "Ice floating on frozen lake, fish alive underneath, winter light, scientific illustration, digital art",
    },
    {
        "fact": "Cleopatra visse piu vicino alla costruzione della Pizza Hut che a quella delle Piramidi di Giza.",
        "caption": "Cleopatra e piu vicina a noi che alle Piramidi.\n\nLe Piramidi furono costruite circa 2.500 anni prima di Cleopatra. Lei mori nel 30 a.C., appena 2.000 anni prima di oggi.\nLa storia e piu strana di quanto pensiamo.\n\nQuale fatto storico ti ha sempre spiazzato?",
        "hashtags": ["storia", "egitto", "cleopatra", "piramidi", "curiosita", "mrcuriously", "fatticuriosi"],
        "image_prompt": "Cleopatra standing near pyramids at sunset, surreal timeline visualization, golden light, digital art",
    },
    {
        "fact": "Il cuore di un gambero si trova nella sua testa. Piu precisamente nel cefalotorace.",
        "caption": "Il cuore del gambero e nella testa.\n\nNel gambero, come in molti crostacei, il cuore non e nel torace ma nel cefalotorace, la parte anteriore del corpo.\nL anatomia degli invertebrati sfida ogni nostra intuizione.\n\nQuale animale ti sembra piu alieno sul nostro pianeta?",
        "hashtags": ["gambero", "biologia", "natura", "scienza", "animali", "mrcuriously", "fatticuriosi"],
        "image_prompt": "Shrimp anatomy cross section showing heart location in cephalothorax, scientific illustration style, digital art",
    },
]


@dataclass
class CaptionResult:
    fact: str
    caption: str
    hashtags: list[str]
    image_prompt: str

    @property
    def full_caption(self) -> str:
        all_tags = list(self.hashtags) + ["AIGenerated"]
        tags = " ".join(f"#{t.lstrip('#')}" for t in all_tags)
        return f"{self.caption}\n\n{tags}"


def generate_caption(cfg: Config, mock: bool = False, recent_facts: list[str] | None = None) -> CaptionResult:
    """Genera caption usando OpenAI (preferito) o Anthropic come fallback.
    Se mock=True o nessuna API key e configurata, usa il pool di fatti mock.
    recent_facts: lista di fatti gia pubblicati per evitare ripetizioni."""
    if mock or (not cfg.openai_api_key and not cfg.anthropic_api_key):
        if not mock:
            print("      [AVVISO] Nessuna API key AI - uso pool di fatti mock.")
        return _mock_caption(recent_facts or [])
    if cfg.openai_api_key:
        return _generate_openai(cfg, recent_facts or [])
    return _generate_anthropic(cfg, recent_facts or [])


def _mock_caption(recent_facts: list[str]) -> CaptionResult:
    """Sceglie un fatto dal pool evitando quelli gia pubblicati di recente."""
    recent_lower = [f.lower()[:60] for f in recent_facts]
    available = [
        f for f in MOCK_FACTS
        if not any(f["fact"].lower()[:60] in r or r in f["fact"].lower()[:60] for r in recent_lower)
    ]
    pool = available if available else MOCK_FACTS
    chosen = random.choice(pool)
    return CaptionResult(
        fact=chosen["fact"],
        caption=chosen["caption"],
        hashtags=chosen["hashtags"],
        image_prompt=chosen["image_prompt"],
    )


def _parse_response(text: str) -> CaptionResult:
    start = text.find("{")
    end = text.rfind("}") + 1
    data = json.loads(text[start:end])
    return CaptionResult(
        fact=data["fact"],
        caption=data["caption"],
        hashtags=data.get("hashtags", []),
        image_prompt=data.get("image_prompt", ""),
    )


def _build_avoid_prompt(recent_facts: list[str]) -> str:
    if not recent_facts:
        return "Genera un fatto curioso."
    topics = "\n".join(f"- {f[:80]}" for f in recent_facts[-10:])
    return f"Genera un fatto curioso. Evita argomenti simili a questi gia pubblicati:\n{topics}"


def _generate_openai(cfg: Config, recent_facts: list[str]) -> CaptionResult:
    from openai import OpenAI

    client = OpenAI(api_key=cfg.openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_avoid_prompt(recent_facts)},
        ],
        temperature=0.9,
        max_tokens=600,
    )
    return _parse_response(response.choices[0].message.content)


def _generate_anthropic(cfg: Config, recent_facts: list[str]) -> CaptionResult:
    import anthropic

    client = anthropic.Anthropic(api_key=cfg.anthropic_api_key)
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=600,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": _build_avoid_prompt(recent_facts)}],
    )
    return _parse_response(message.content[0].text)
