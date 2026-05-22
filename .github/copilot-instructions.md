# Mr. Curiously — Copilot Instructions

## Progetto
**Mr. Curiously** è un bot Python di social media automation che pubblica ogni giorno un fatto curioso su **Instagram** e **TikTok**. La pipeline è completamente automatizzata tramite GitHub Actions (cron 09:00 UTC).

## Stack Tecnologico
- **Python 3.11**, Click CLI, python-dotenv
- **AI**: OpenAI GPT-4o-mini (preferito), Anthropic Claude Haiku (fallback), pool mock (fallback finale)
- **Immagini**: Pillow (branded 1080×1080) con DALL-E 3 opzionale
- **Video**: MoviePy + NumPy (typewriter effect 1080×1920 per TikTok)
- **Storage**: Cloudflare R2 via boto3 (S3-compatible)
- **Instagram**: Meta Graph API v21.0
- **TikTok**: Content Posting API v2 + OAuth 2.0 PKCE
- **Scheduler**: `schedule` lib + GitHub Actions cron

## Struttura
```
src/
├── config.py          # Dataclass Config — carica .env
├── cli.py             # Click CLI: run, dry-run, test-*, schedule
├── generators/
│   ├── caption.py     # LLM caption + hashtag (include #AIGenerated)
│   ├── image.py       # Immagine post 1080×1080
│   ├── video.py       # Video TikTok 1080×1920 typewriter
│   └── profile.py     # Immagine profilo
├── publishers/
│   ├── instagram.py   # Graph API v21.0
│   └── tiktok.py      # Content Posting API v2 (ai_generated_content: true)
├── storage/
│   ├── r2.py          # Upload su Cloudflare R2
│   └── history.py     # Anti-ripetizione su R2 (max 60 voci)
└── scheduler/
    └── daily.py       # Pipeline 5 step
docs/                  # GitHub Pages: sito legale (Privacy, Terms) + OAuth entry point TikTok
```

## Convenzioni
- **Lingua contenuto**: fatto e caption in italiano; `image_prompt` in inglese. I nomi di variabili, commenti nel codice e docstring sono in inglese.
- **Label AI obbligatorie**: tutti i post includono `#AIGenerated` nell'hashtag (Instagram) e `ai_generated_content: True` nel payload TikTok. Non rimuovere questi campi.
- **Credenziali**: non inserire mai secrets, token o chiavi API nel codice sorgente. Usare sempre `.env` locale (non committato) o GitHub Actions Secrets.
- **TikTok opzionale**: il publisher TikTok si attiva solo se `TIKTOK_ACCESS_TOKEN` è presente nel config. Se mancante, la pipeline continua senza errori pubblicando solo su Instagram.
- **Sito docs/**: le pagine in `docs/` sono servite da GitHub Pages. Modifiche a Privacy Policy e Terms of Service devono mantenere il nome "Mr. Curiously" nei titoli H1 e il favicon `mrcuriously.png`.

## Variabili d'Ambiente Chiave
```
OPENAI_API_KEY, ANTHROPIC_API_KEY
IG_USER_ID, IG_ACCESS_TOKEN, IG_USERNAME
R2_ENDPOINT, R2_ACCESS_KEY, R2_SECRET_KEY, R2_BUCKET, R2_PUBLIC_URL
TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_ACCESS_TOKEN, TIKTOK_OPEN_ID
```

## Stato Attuale
> Nota: questa sezione riflette lo stato al momento dell'ultimo aggiornamento e può essere obsoleta.
- ✅ Pipeline Instagram in produzione (GitHub Actions cron affidabile)
- ⏳ App TikTok Developer Portal in review (risubmessa il 22/05/2026 dopo correzioni docs)
- ❌ Token TikTok non ancora ottenuti — secrets GitHub Actions TikTok non ancora configurati
