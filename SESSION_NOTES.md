# Session Notes — Mr. Curiously

---

## Session 2025-07-14

### What was done
- Aggiunto file verifica dominio TikTok Developer Portal (`docs/tiktokrZ2JSLP6hLtqiBleFhYrohfMTUtLSIqY.txt`) e pushato su GitHub
- Creato `tiktok_oauth.py`: server Flask-less su porta 8080 + PKCE state, scambia `code` → `access_token` e salva automaticamente nel `.env`
- Installato e configurato **ngrok v3.39.2** per tunnel HTTPS → localhost:8080
- Aggiunto redirect URI `https://gave-overrun-progeny.ngrok-free.dev/callback` nel TikTok Developer Portal (⚠️ ngrok free cambia ad ogni riavvio)
- Creato account TikTok `@mr.curiously` e aggiunto come **sandbox tester**
- Aggiunti `TIKTOK_CLIENT_KEY` e `TIKTOK_CLIENT_SECRET` nel `.env`
- Pushati file verifica Content Posting API (`docs/tiktokdarNSApa2EWTH1FjuAj1k1p5QjYvQJ2q.txt`) e Terms/Privacy URL (`docs/tiktokqGomWcXMhCJNE9kXyfHNliQE3Cj9nUdG.txt`)
- Verificati Terms of Service URL e Privacy Policy URL sul TikTok Developer Portal ✅
- Registrato video demo dell'app → **Submit for Review** completato ✅
- **App TikTok attualmente IN REVIEW** (attesa 1–7 giorni lavorativi)

### Decisions made
- **Scelta: stdlib `http.server` invece di Flask** per `tiktok_oauth.py` — zero dipendenze extra, usa solo `requests` già presente
- **Scelta: ngrok gratuito** per il redirect URI HTTPS — sufficiente per la fase di setup OAuth iniziale; l'URL cambia ad ogni riavvio (limitazione nota)
- **Scelta: salvataggio token direttamente nel `.env`** — `save_tokens_to_env()` usa regex per replace-or-append; evita copie manuali post-OAuth
- `TIKTOK_CLIENT_KEY = awww7dzsi0qyfjcg` — registrato in note (non commit in chiaro su repo pubblico)
- Scope richiesti: `user.info.basic,video.upload`

### Current status
- ✅ App TikTok creata e in review
- ✅ File di verifica dominio, Terms e Privacy pushati e verificati
- ✅ `tiktok_oauth.py` funzionante (flusso testato fino a redirect; token exchange verificabile solo dopo approvazione app)
- ✅ `TIKTOK_CLIENT_KEY` e `TIKTOK_CLIENT_SECRET` nel `.env`
- ⏳ **App in review** — nessuna azione possibile finché TikTok non approva
- ❌ `TIKTOK_ACCESS_TOKEN` e `TIKTOK_OPEN_ID` non ancora ottenuti
- ❌ Publisher TikTok non ancora integrato nel pipeline (`src/publishers/tiktok.py` da creare)
- ❌ GitHub Actions secrets TikTok non ancora configurati

### Next steps
1. **Attendere email di approvazione TikTok** (1–7 giorni lavorativi)
2. **Flusso OAuth post-approvazione**:
   - Aggiornare `REDIRECT_URI` in `tiktok_oauth.py` (ngrok free URL cambia → riavviare ngrok e aggiornare Developer Portal)
   - In alternativa: usare ngrok a pagamento (URL fisso) o un redirect URI su dominio stabile
   - Eseguire `python tiktok_oauth.py` → completare il flusso → ottenere `TIKTOK_ACCESS_TOKEN` e `TIKTOK_OPEN_ID`
3. **Creare `src/publishers/tiktok.py`** — publisher video TikTok via Content Posting API v2
4. **Aggiungere comando CLI** `python -m src.cli test-tiktok`
5. **Aggiungere secrets GitHub Actions**: `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET`, `TIKTOK_ACCESS_TOKEN`, `TIKTOK_OPEN_ID`
6. **Test pipeline completa** con TikTok: `python -m src.cli run`
7. **Future**: implementare refresh token (il token TikTok scade)

### Files changed
- `tiktok_oauth.py` — **CREATO**: server OAuth locale port 8080, scambia authorization code, salva tokens nel .env
- `docs/tiktokrZ2JSLP6hLtqiBleFhYrohfMTUtLSIqY.txt` — file verifica dominio TikTok (pushato)
- `docs/tiktokdarNSApa2EWTH1FjuAj1k1p5QjYvQJ2q.txt` — file verifica Content Posting API
- `docs/tiktokqGomWcXMhCJNE9kXyfHNliQE3Cj9nUdG.txt` — file verifica Terms/Privacy URL
- `.env` — aggiunti `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET` (non in repo)
- `README.md` — aggiunta sezione **TikTok Setup** con stato attuale

---

## Session 2026-05-21

### What was done
- Prima esecuzione della GitHub Action schedulata: il cron (`0 9 * * *`) **non ha sparato automaticamente** alle 11:00 ora italiana
- L'action è stata avviata manualmente alle ~11:40 tramite `workflow_dispatch` dal pannello GitHub Actions
- Analisi della causa: il repository aveva solo 2 giorni di storia (tutti i commit dal 20-21 maggio); GitHub può saltare la prima esecuzione schedulata di un workflow appena creato

### Decisions made
- **Aspettare domani** per verificare se il cron parte autonomamente alla seconda occorrenza
- Se domani non parte: configurare trigger esterno via **cron-job.org** (gratuito) che chiama `workflow_dispatch` via GitHub API alle 11:00 ogni giorno

### Current status
- ✅ Pipeline Instagram funzionante (confermato dall'esecuzione manuale di oggi)
- ⏳ Verifica affidabilità cron GitHub Actions — da confermare domani 22/05/2026
- ⏳ App TikTok ancora in review (sottomessa il 2026-05-20)

### Next steps
1. **Domani 22/05**: verificare se la GitHub Action parte autonomamente alle 11:00
   - Se sì → tutto ok, cron affidabile
   - Se no → configurare cron-job.org come trigger esterno via GitHub API `workflow_dispatch`
2. **Post-approvazione TikTok**: completare OAuth, aggiungere secrets GitHub Actions, testare pipeline completa

---

## Session 2026-05-22

### What was done
- **Cron GitHub Actions confermato autonomo** ✅ — la seconda esecuzione schedulata è partita automaticamente alle 09:00 UTC; il dubbio della sessione precedente è risolto
- Ricevuta email di rifiuto da TikTok Developer Review con le seguenti richieste:
  - App icon visibile come favicon e in header su Privacy Policy e Terms of Service
  - Titoli H1 che includano il nome app ("Mr. Curiously Privacy Policy" / "Mr. Curiously Terms of Service")
  - Privacy Policy e Terms of Service insufficienti (non menzionavano l'app per nome)
  - Nessun login entry point sul sito
  - Website non sufficientemente sviluppato
- Applicate tutte le correzioni al sito `docs/`:
  - `index.html` ridisegnato come sito multi-sezione con header con logo
  - Aggiunto bottone **"Connect with TikTok"** (OAuth entry point) con `client_key=awww7dzsi0qyfjcg`
  - Aggiunta `callback.html` per gestire il redirect OAuth di TikTok (mostra il codice di autorizzazione)
  - `privacy.html` riscritta con 8 sezioni dettagliate che menzionano l'app per nome
  - `terms.html` riscritta con 10 sezioni (disclaimer, limitazioni, piattaforme terze)
  - Favicon `mrcuriously.png` aggiunta a tutte le pagine
  - Header con logo e nome app su tutte le pagine
- App TikTok **risubmessa in review** (22/05/2026)
- Aggiunta label AI obbligatoria su TikTok: `ai_generated_content: True` in `tiktok.py`
- Aggiunta label AI su Instagram: hashtag `#AIGenerated` in `caption.py` via `full_caption`
- Creato `.github/copilot-instructions.md` per contesto automatico nelle sessioni future

### Decisions made
- **Redirect URI stabile su GitHub Pages** (`callback.html`) — eliminata la dipendenza da ngrok per il flusso OAuth; l'URL è permanente e non cambia
- **`#AIGenerated` in `full_caption`** — si applica a tutti i post (mock e LLM) senza duplicare logica
- **`ai_generated_content: True` sempre attivo** in TikTok publisher — obbligatorio per policy, nessun motivo per renderlo configurabile

### Current status
- ✅ Pipeline Instagram in produzione e affidabile (cron GitHub Actions confermato)
- ✅ Publisher TikTok completo con label AI
- ✅ Sito docs corretto e risubmesso per review TikTok
- ✅ Redirect OAuth stabile su GitHub Pages
- ⏳ App TikTok in review (seconda submission 22/05/2026)
- ❌ `TIKTOK_ACCESS_TOKEN` e `TIKTOK_OPEN_ID` non ancora ottenuti
- ❌ GitHub Actions secrets TikTok non ancora configurati

### Next steps
1. **Attendere approvazione TikTok** (1–7 giorni lavorativi)
2. **Post-approvazione**: cliccare "Connect with TikTok" su GitHub Pages → completare OAuth → copiare token dal `callback.html`
3. **Aggiungere secrets GitHub Actions**: `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET`, `TIKTOK_ACCESS_TOKEN`, `TIKTOK_OPEN_ID`
4. **Testare pipeline TikTok**: `python -m src.cli test-tiktok`
5. **Future**: implementare refresh token automatico (il token TikTok scade periodicamente)

### Files changed
- `docs/index.html` — ridisegnato: header con logo, sezione About, bottone "Connect with TikTok", sezione Legal
- `docs/privacy.html` — riscritta: 8 sezioni, favicon, header con logo, titolo H1 corretto
- `docs/terms.html` — riscritta: 10 sezioni, favicon, header con logo, titolo H1 corretto
- `docs/callback.html` — **CREATO**: gestisce redirect OAuth TikTok, mostra authorization code
- `docs/mrcuriously.png` — aggiunto in `docs/` per favicon e header
- `src/publishers/tiktok.py` — aggiunto `ai_generated_content: True` in `post_info`
- `src/generators/caption.py` — `full_caption` aggiunge `#AIGenerated` a ogni post
- `.github/copilot-instructions.md` — **CREATO**: contesto progetto per sessioni future

---
