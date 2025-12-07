# Sync Spotify ↔ YouTube Music su Replit

Questo progetto contiene uno script Python (`sync_playlists.py`) che mantiene sincronizzate in tempo reale le tue playlist tra Spotify e YouTube Music, in entrambe le direzioni. È pensato per essere eseguito su [Replit](https://replit.com) con le variabili d'ambiente impostate nelle *Secrets* del progetto.

## Cosa fa
- Copia i brani mancanti da una playlist Spotify a una playlist YouTube Music.
- Copia i brani mancanti da YouTube Music a Spotify (bidirezionale per impostazione predefinita).
- Usa ricerche intelligenti per trovare il match migliore su entrambi i servizi.

## Configurazione rapida su Replit
1. **Crea un nuovo Repl** basato su template *Python* e importa questo repository da GitHub.
   - Se usi GitHub, lavora direttamente sul branch **main** per evitare di dover unire branch separati quando il Repl viene aggiornato: imposta il branch di default a `main` e fai push lì per avere il codice subito disponibile all'import.
2. Apri la sezione **Tools → Secrets** e aggiungi le seguenti variabili:
   - `SPOTIFY_CLIENT_ID` e `SPOTIFY_CLIENT_SECRET`: presi dalla tua app su [Spotify for Developers](https://developer.spotify.com/dashboard/).
   - `SPOTIFY_REFRESH_TOKEN`: ottienilo con il tuo account (scope `playlist-read-private playlist-modify-public playlist-modify-private`).
   - `SPOTIFY_REDIRECT_URI`: lo stesso URI registrato nella dashboard Spotify. Puoi usare `http://localhost:8888/callback` in locale oppure l'URL del tuo Repl con `/callback` (es. `https://<il-tuo-nome>.<user>.repl.co/callback`).
   - `SPOTIFY_PLAYLIST_ID`: ID della playlist sorgente/destinazione su Spotify (solo la parte finale dell'URL o l'URI completo).
   - `YTMUSIC_COOKIE`: stringa di autenticazione `ytmusicapi` esportata dal tuo browser (header `cookie` completo dalla scheda YouTube Music).
   - `YTMUSIC_PLAYLIST_ID`: ID della playlist su YouTube Music (l'ID dopo `?list=` nell'URL).
   - `SYNC_DIRECTION` *(opzionale)*: `both` (default), `spotify_to_yt` oppure `yt_to_spotify` per limitare la direzione di sincronizzazione.
3. Installa le dipendenze con `pip install -r requirements.txt` (su Replit viene eseguito automaticamente al primo run).
4. Avvia lo script con `python sync_playlists.py`. Il log finale mostrerà quanti brani sono stati aggiunti su ciascuna piattaforma.

## Come funziona
- Lo script legge le playlist, costruisce una chiave `titolo + artista` e aggiunge solo i brani che non sono già presenti sull'altra piattaforma.
- Per ogni brano mancante, effettua una ricerca (`search`) e usa il primo risultato disponibile prima di aggiungerlo alla playlist.
- Gli inserimenti sono batched per rispettare i limiti API (100 elementi per Spotify, 99 per YouTube Music).

## Esecuzione locale (facoltativa)
1. Crea un virtualenv: `python -m venv .venv && source .venv/bin/activate`.
2. Installa le dipendenze: `pip install -r requirements.txt`.
3. Esporta le variabili d'ambiente elencate sopra e lancia `python sync_playlists.py`.

## Come ottenere playlist ID e token
### Spotify
1. **Crea l'app** su [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) e aggiungi uno o più *Redirect URIs* in **Settings → Redirect URIs**:
   - `http://localhost:8888/callback` per uso locale.
   - `https://<il-tuo-nome>.<user>.repl.co/callback` se fai l'OAuth dal Repl (sostituisci con il dominio del tuo Repl).
   Salva le modifiche, altrimenti il login fallirà.
2. **Recupera il refresh token automaticamente**: esegui `python spotify_refresh_token.py` su Replit o in locale e segui il link di autorizzazione. Copia il codice dalla barra degli indirizzi dopo il redirect e incollalo nel prompt; il tool stamperà `SPOTIFY_REFRESH_TOKEN` pronto da salvare nelle Secrets. Se usi il Repl, assicurati che il redirect URI usato sia uno di quelli registrati sopra.
3. **Playlist ID**: apri la playlist su Spotify → *Altro* → *Condividi* → *Copia link della playlist*. L'ID è la parte finale dell'URL dopo `playlist/` (es. `https://open.spotify.com/playlist/<ID>`).

### YouTube Music
1. Visita [music.youtube.com](https://music.youtube.com) con il browser loggato.
2. Apri **Strumenti Sviluppatore** (F12) → tab *Network* e filtra per `browse`.
3. Aggiorna la pagina, clicca su una richiesta `browse`, copia l'header `cookie` completo e incollalo come `YTMUSIC_COOKIE` nelle Secrets.
4. **Playlist ID**: apri la playlist su YouTube Music e copia l'ID dopo `?list=` nell'URL.

### Automatizzare i run su Replit
- Questo repository contiene un file `.replit` con `alwaysOn = true` per mantenere il Repl attivo di default.
- Puoi comunque aggiungere un **Scheduled task** (`.replit` → *Scheduled tasks*) che esegua `python sync_playlists.py` ogni pochi minuti se vuoi una cadenza specifica.
- In alternativa, usa il tab *Shell* e lancia `while true; do python sync_playlists.py; sleep 300; done` per avere un ciclo continuo (consuma le risorse del Repl attivo).

## Note importanti
- Assicurati che le playlist siano *tue* o che tu abbia i permessi per modificarle.
- Se un brano non viene trovato su una piattaforma, viene semplicemente ignorato nel ciclo successivo.
- Conserva i token e i cookie solo in ambienti sicuri (Secrets di Replit) per proteggere il tuo account.
