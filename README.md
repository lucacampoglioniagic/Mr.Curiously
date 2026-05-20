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

| Variabile | Descrizione |
|---|---|
| `IG_USER_ID` | ID utente Instagram Business |
| `IG_ACCESS_TOKEN` | Token Graph API (long-lived) |
| `IG_USERNAME` | Handle Instagram (es. `mr.curiously`) |
| `R2_ACCOUNT_ID` | Cloudflare Account ID |
| `R2_ACCESS_KEY` / `R2_SECRET_KEY` | Credenziali R2 |
| `R2_BUCKET` | Nome bucket R2 |
| `R2_PUBLIC_URL` | URL pubblico del bucket |
| `R2_ENDPOINT` | Endpoint S3-compat R2 |
| `OPENAI_API_KEY` | *(opzionale)* Abilita caption GPT-4o-mini + DALL-E 3 |
| `ANTHROPIC_API_KEY` | *(opzionale)* Fallback caption con Claude Haiku |

> Se nessuna API key AI è configurata, la pipeline usa una caption mock (utile per test).

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
```

## Struttura del progetto

```
src/
  config.py              # carica .env, espone Config tipizzato
  cli.py                 # comandi Click (run, dry-run, test-instagram, schedule)
  generators/
    caption.py           # genera fatto + caption + hashtag via LLM
    image.py             # genera immagine (Pillow branded o DALL-E 3)
  publishers/
    instagram.py         # pubblica su Instagram via Graph API v21.0
  storage/
    r2.py                # upload su Cloudflare R2
  scheduler/
    daily.py             # pipeline 4-step + scheduler giornaliero
```

## Automazione giornaliera (GitHub Actions)

Il workflow `.github/workflows/daily.yml` pubblica automaticamente alle **09:00 UTC (11:00 ora italiana)** ogni giorno.

### Setup

1. Crea un repository su GitHub e fai push del progetto
2. Vai su **Settings → Secrets and variables → Actions** e aggiungi tutti i segreti:

| Secret | Valore |
|---|---|
| `IG_USER_ID` | ID utente Instagram |
| `IG_ACCESS_TOKEN` | Token Graph API |
| `IG_USERNAME` | Handle Instagram |
| `R2_ACCOUNT_ID` | Cloudflare Account ID |
| `R2_ACCESS_KEY` | R2 Access Key |
| `R2_SECRET_KEY` | R2 Secret Key |
| `R2_BUCKET` | Nome bucket |
| `R2_PUBLIC_URL` | URL pubblico bucket |
| `R2_ENDPOINT` | Endpoint S3-compat |
| `OPENAI_API_KEY` | *(opzionale)* Per caption AI + DALL-E 3 |
| `ANTHROPIC_API_KEY` | *(opzionale)* Fallback caption AI |

3. Il workflow parte automaticamente ogni giorno. Per lanciarlo manualmente: **Actions → Daily Post → Run workflow**



- **Senza `OPENAI_API_KEY`**: immagine branded generata con Pillow — sfondo con gradiente blu scuro, particelle, punto interrogativo decorativo, testo del fatto e footer `@mr.curiously`
- **Con `OPENAI_API_KEY`**: usa DALL-E 3 con il prompt generato dall'LLM; Pillow come fallback automatico in caso di errore

### Nota sui font (Pillow)

Il renderer Pillow usa font di sistema (Arial su Windows). **Non supporta emoji Unicode** — caratteri come `🧠` o `✦` vengono renderizzati come quadratini (`□`).  
Per usare emoji nelle immagini è necessario un font dedicato (es. Noto Color Emoji). Fino ad allora, nel testo dell'immagine si usano solo caratteri ASCII.
