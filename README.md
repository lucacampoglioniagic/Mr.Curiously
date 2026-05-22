# Mr. Curiously — Auto Content Publisher

Pipeline automatica che ogni giorno:
1. Genera un "fatto curioso" con LLM (caption + hashtag + `#AIGenerated`)
2. Genera un'immagine 1080×1080 (Pillow branded o DALL-E 3) + video 1080×1920 (typewriter TikTok)
3. Carica il media su Cloudflare R2
4. Pubblica su Instagram
5. Pubblica su TikTok *(token in attesa di approvazione app)*

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
| `META_APP_ID` | ⬜ | App ID Meta (usato dal workflow CI) |
| `META_APP_SECRET` | ⬜ | App secret Meta (usato dal workflow CI) |
| `TIKTOK_CLIENT_KEY` | ⬜ | App key TikTok Developer Portal |
| `TIKTOK_CLIENT_SECRET` | ⬜ | App secret TikTok Developer Portal |
| `TIKTOK_ACCESS_TOKEN` | ⬜ | Token OAuth TikTok (ottenuto via `tiktok_oauth.py`) |
| `TIKTOK_OPEN_ID` | ⬜ | Open ID utente TikTok (ottenuto via `tiktok_oauth.py`) |

> Se nessuna API key AI è configurata, la pipeline usa un pool di 15 fatti mock rotativi.

## Comandi CLI

```bash
# Genera il video TikTok (test locale)
python -m src.cli test-video

# Pubblica un post reale (pipeline completa)
python -m src.cli run

# Prova la pipeline senza pubblicare
python -m src.cli dry-run

# Test end-to-end: immagine → R2 → Instagram
python -m src.cli test-instagram

# Test pubblicazione TikTok (disponibile dopo approvazione app)
python -m src.cli test-tiktok

# Avvia lo scheduler giornaliero (pubblica alle 09:00)
python -m src.cli schedule

# Genera l'immagine del profilo Instagram
python -m src.cli profile-image
```

## Struttura del progetto

```
src/
  config.py              # carica .env, espone Config tipizzato
  cli.py                 # comandi Click (run, dry-run, test-instagram, test-tiktok, test-video, schedule, profile-image)
  generators/
    caption.py           # genera fatto + caption + hashtag via LLM; aggiunge #AIGenerated a tutti i post
    image.py             # genera immagine post 1080×1080 (Pillow branded o DALL-E 3)
    video.py             # genera video TikTok 1080×1920 con effetto typewriter (MoviePy)
    profile.py           # genera immagine profilo Instagram 1080×1080
  publishers/
    instagram.py         # pubblica su Instagram via Graph API v21.0
    tiktok.py            # pubblica su TikTok via Content Posting API v2 (ai_generated_content: true)
  storage/
    r2.py                # upload su Cloudflare R2
    history.py           # storico pubblicazioni su R2 (history/published.json)
  scheduler/
    daily.py             # pipeline 5-step + scheduler giornaliero
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

---

## Etichette AI (Policy compliance)

Tutti i contenuti pubblicati da Mr. Curiously includono etichette AI obbligatorie:

- **Instagram**: hashtag `#AIGenerated` aggiunto automaticamente a ogni caption (via `full_caption` in `caption.py`)
- **TikTok**: campo `ai_generated_content: true` incluso nel payload dell'API Content Posting (via `tiktok.py`)

Questo è richiesto dalle policy di entrambe le piattaforme per contenuti generati o modificati con AI.

---

## TikTok Setup

> **Stato attuale: App risubmessa in review ⏳** — seconda submission il 22/05/2026 dopo correzioni al sito `docs/` (richieste dal reviewer TikTok). In attesa di approvazione (1–7 giorni lavorativi).

> **Nota**: il redirect URI è ora stabile su GitHub Pages (`https://lucacampoglioniagic.github.io/Mr.Curiously/callback.html`) — non è più necessario ngrok per il flusso OAuth.

### Come funziona il flusso OAuth

Lo script `tiktok_oauth.py` implementa un server locale OAuth su **porta 8080** che:
1. Reindirizza l'utente a TikTok per l'autorizzazione
2. Riceve il callback con il `code`
3. Scambia il `code` con `access_token` + `open_id`
4. Salva i token automaticamente nel `.env`

### Setup iniziale (da completare dopo approvazione app)

```bash
# 1. Assicurarsi che TIKTOK_CLIENT_KEY e TIKTOK_CLIENT_SECRET siano nel .env

# 2. Aprire la homepage del sito e cliccare "Connect with TikTok"
#    https://lucacampoglioniagic.github.io/Mr.Curiously/
#    → TikTok reindirizza su callback.html con il codice di autorizzazione

# 3. In alternativa, avviare il server OAuth locale (usa ngrok se il redirect URI è localhost)
python tiktok_oauth.py

# 4. Completare il flusso nel browser
# → TIKTOK_ACCESS_TOKEN e TIKTOK_OPEN_ID vengono salvati automaticamente nel .env
```

> ⚠️ Il redirect URI stabile è `https://lucacampoglioniagic.github.io/Mr.Curiously/callback.html` (GitHub Pages).
> Se si usa `tiktok_oauth.py` in locale, aggiornare il redirect URI nel Developer Portal con l'URL ngrok corrente.

### Secrets GitHub Actions da aggiungere

Dopo aver ottenuto i token, aggiungere in **Settings → Secrets and variables → Actions**:

| Secret | Descrizione |
|---|---|
| `TIKTOK_CLIENT_KEY` | App key dal Developer Portal |
| `TIKTOK_CLIENT_SECRET` | App secret dal Developer Portal |
| `TIKTOK_ACCESS_TOKEN` | Token OAuth (da `tiktok_oauth.py`) |
| `TIKTOK_OPEN_ID` | Open ID utente (da `tiktok_oauth.py`) |
