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
│   └── tiktok.py      # Content Posting API v2 (con ai_generated_content: true)
├── storage/
│   ├── r2.py          # Upload su Cloudflare R2
│   └── history.py     # Anti-ripetizione su R2 (max 60 voci)
└── scheduler/
    └── daily.py       # Pipeline 5 step
docs/                  # GitHub Pages — sito legale + OAuth entry point
```

## Convenzioni
- Lingua: **italiano** per fatto/caption, **inglese** per image_prompt e codice/commenti
- Tutti i post includono `#AIGenerated` (policy TikTok e Meta)
- TikTok publisher usa `ai_generated_content: True` nel payload API
- I segreti non vanno mai nel codice — usare `.env` locale o GitHub Secrets
- Il TikTok publisher salta silenziosamente se `TIKTOK_ACCESS_TOKEN` non è configurato

## Variabili d'Ambiente Chiave
```
OPENAI_API_KEY, ANTHROPIC_API_KEY
IG_USER_ID, IG_ACCESS_TOKEN, IG_USERNAME
R2_ENDPOINT, R2_ACCESS_KEY, R2_SECRET_KEY, R2_BUCKET, R2_PUBLIC_URL
TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_ACCESS_TOKEN, TIKTOK_OPEN_ID
```

## Stato Attuale (Maggio 2026)
- ✅ Pipeline Instagram in produzione
- ⏳ App TikTok Developer Portal in review (risubmessa dopo correzioni docs)
- ❌ Token TikTok non ancora disponibili
