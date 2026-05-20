# Mr. Curiously — Auto Content Publisher

Pipeline automatica che ogni giorno:
1. Genera un "fatto curioso" con LLM (caption + hashtag)
2. Genera un'immagine 1080×1080 (Pillow branded o DALL-E 3)
3. Carica il media su Cloudflare R2
4. Pubblica su Instagram
5. *(in arrivo)* Pubblica su TikTok

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
| `TIKTOK_CLIENT_KEY` | ⬜ | App key TikTok Developer Portal |
| `TIKTOK_CLIENT_SECRET` | ⬜ | App secret TikTok Developer Portal |
| `TIKTOK_ACCESS_TOKEN` | ⬜ | Token OAuth TikTok (ottenuto via `tiktok_oauth.py`) |
| `TIKTOK_OPEN_ID` | ⬜ | Open ID utente TikTok (ottenuto via `tiktok_oauth.py`) |

> Se nessuna API key AI è configurata, la pipeline usa un pool di 15 fatti mock rotativi.

## Comandi CLI

```bash
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

---

## TikTok Setup

> **Stato attuale: App in review ⏳** — in attesa di approvazione TikTok (1–7 giorni lavorativi).

### Come funziona il flusso OAuth

Lo script `tiktok_oauth.py` implementa un server locale OAuth su **porta 8080** che:
1. Reindirizza l'utente a TikTok per l'autorizzazione
2. Riceve il callback con il `code`
3. Scambia il `code` con `access_token` + `open_id`
4. Salva i token automaticamente nel `.env`

### Setup iniziale (da completare dopo approvazione app)

```bash
# 1. Assicurarsi che TIKTOK_CLIENT_KEY e TIKTOK_CLIENT_SECRET siano nel .env

# 2. Avviare ngrok per creare un tunnel HTTPS verso localhost:8080
ngrok http 8080
# Copiare l'URL HTTPS generato (es. https://xxxx.ngrok-free.dev)

# 3. Aggiornare REDIRECT_URI in tiktok_oauth.py con il nuovo URL ngrok
#    Aggiungere lo stesso URL nel TikTok Developer Portal → Login Kit → Redirect URIs

# 4. Avviare il server OAuth
python tiktok_oauth.py

# 5. Aprire http://localhost:8080 nel browser e completare il flusso
# → TIKTOK_ACCESS_TOKEN e TIKTOK_OPEN_ID vengono salvati automaticamente nel .env
```

> ⚠️ **Nota ngrok free**: l'URL HTTPS cambia ad ogni riavvio di ngrok. Per un redirect URI stabile, considera ngrok a pagamento o un dominio fisso.

### Secrets GitHub Actions da aggiungere

Dopo aver ottenuto i token, aggiungere in **Settings → Secrets and variables → Actions**:

| Secret | Descrizione |
|---|---|
| `TIKTOK_CLIENT_KEY` | App key dal Developer Portal |
| `TIKTOK_CLIENT_SECRET` | App secret dal Developer Portal |
| `TIKTOK_ACCESS_TOKEN` | Token OAuth (da `tiktok_oauth.py`) |
| `TIKTOK_OPEN_ID` | Open ID utente (da `tiktok_oauth.py`) |
