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
