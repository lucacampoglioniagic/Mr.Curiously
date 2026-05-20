# Mr. Curiously — Auto Content Publisher

Pipeline automatica che ogni giorno:
1. Genera un "fatto curioso" con LLM (caption + hashtag)
2. Genera un'immagine 1080×1080 (Pillow branded o DALL-E 3)
3. Carica il media su Cloudflare R2
4. Pubblica su Instagram

## Setup

```bash
# 1. Copia e popola le credenziali
cp .env.example .env

# 2. Crea e attiva il virtualenv
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# 3. Installa le dipendenze
pip install -r requirements.txt

# 4. Verifica end-to-end (pubblica un post di test)
python -m src.cli test-instagram
```

## Variabili d'ambiente (`.env`)

| Variabile | Obbligatoria | Descrizione |
|---|---|---|
| `IG_USER_ID` | ✅ | ID utente Instagram Business |
| `IG_ACCESS_TOKEN` | ✅ | Token Graph API (long-lived) |
| `R2_ACCOUNT_ID` | ✅ | Cloudflare Account ID |
| `R2_ACCESS_KEY` / `R2_SECRET_KEY` | ✅ | Credenziali R2 |
| `R2_BUCKET` | ✅ | Nome bucket R2 |
| `R2_PUBLIC_URL` | ✅ | URL pubblico del bucket |
| `R2_ENDPOINT` | ✅ | Endpoint S3-compat R2 |
| `IG_USERNAME` | ⬜ | Handle Instagram (usato solo nel log) |
| `OPENAI_API_KEY` | ⬜ | Abilita caption GPT-4o-mini + immagini DALL-E 3 |
| `ANTHROPIC_API_KEY` | ⬜ | Fallback caption con Claude Haiku |

> Se nessuna API key AI è configurata, la pipeline usa un pool di 15 fatti mock rotativi.

## Comandi CLI

```bash
# Pubblica un post reale (pipeline completa)
python -m src.cli run

# Prova la pipeline senza pubblicare
python -m src.cli dry-run

# Test end-to-end: immagine → R2 → Instagram
python -m src.cli test-instagram

# Avvia lo scheduler giornaliero (pubblica alle 09:00)
python -m src.cli schedule

# Genera l'immagine del profilo Instagram
python -m src.cli profile-image
```

## Struttura del progetto

```
src/
  config.py              # carica .env, espone Config tipizzato
  cli.py                 # comandi Click (run, dry-run, test-instagram, schedule, profile-image)
  generators/
    caption.py           # genera fatto + caption + hashtag via LLM (pool mock se no API key)
    image.py             # genera immagine post (Pillow branded o DALL-E 3)
    profile.py           # genera immagine profilo Instagram 1080x1080
  publishers/
    instagram.py         # pubblica su Instagram via Graph API v21.0
  storage/
    r2.py                # upload su Cloudflare R2
    history.py           # storico pubblicazioni su R2 (history/published.json)
  scheduler/
    daily.py             # pipeline 4-step + scheduler giornaliero
```

## Anti-ripetizione

Lo storico delle pubblicazioni viene salvato su R2 in `history/published.json` (max 60 voci).

- **Con mock**: il pool di 15 fatti esclude quelli già pubblicati di recente
- **Con LLM**: i fatti recenti vengono passati al modello come contesto per evitare argomenti simili
- Lo storico persiste tra i run di GitHub Actions automaticamente

## Automazione giornaliera (GitHub Actions)

Il workflow `.github/workflows/daily.yml` pubblica automaticamente alle **09:00 UTC (11:00 ora italiana)** ogni giorno.

### Setup

1. Crea un repository su GitHub e fai push del progetto
2. Vai su **Settings → Secrets and variables → Actions** e aggiungi gli 8 secrets obbligatori (vedi tabella sopra)
3. Il workflow parte automaticamente ogni giorno. Per lanciarlo manualmente: **Actions → Daily Post → Run workflow**

## Generazione immagine post

- **Senza `OPENAI_API_KEY`**: immagine branded con Pillow — gradiente blu scuro, particelle, punto interrogativo decorativo, testo del fatto, footer `@mr.curiously`
- **Con `OPENAI_API_KEY`**: DALL-E 3 con prompt generato dall'LLM; Pillow come fallback automatico

### Nota sui font (Pillow)

Il renderer Pillow usa font di sistema (Arial su Windows, DejaVu/Liberation su Linux). **Non supporta emoji Unicode** — caratteri come `🧠` vengono renderizzati come quadratini (`□`). Nel testo delle immagini si usano solo caratteri ASCII.
