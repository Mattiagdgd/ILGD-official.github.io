# Sync Spotify ↔ YouTube Music su Replit

Questo progetto contiene uno script Python (`sync_playlists.py`) che mantiene sincronizzate in tempo reale le tue playlist tra Spotify e YouTube Music, in entrambe le direzioni. È pensato per essere eseguito su [Replit](https://replit.com) con le variabili d'ambiente impostate nelle *Secrets* del progetto.

## Cosa fa
- Copia i brani mancanti da una playlist Spotify a una playlist YouTube Music.
- Copia i brani mancanti da YouTube Music a Spotify (bidirezionale per impostazione predefinita).
- Usa ricerche intelligenti per trovare il match migliore su entrambi i servizi.

## Configurazione rapida su Replit
1. **Crea un nuovo Repl** basato su template *Python* e importa questo repository da GitHub.
   - Se usi GitHub, lavora direttamente sul branch **main** per evitare di dover unire branch separati quando il Repl viene aggiornato: imposta il branch di default a `main` e fai push lì per avere il codice subito disponibile all'import.
2. **Valori preconfigurati (auto-fill)**: lo script inserisce automaticamente questi valori se non trovi le variabili nelle *Secrets* del Repl:
   - `SPOTIFY_CLIENT_ID`: `4a2e9bd9c5bb4c05a0b05f1062ac7e70`
   - `SPOTIFY_CLIENT_SECRET`: `650e7d4a91cc4fae896bc3f0b0ff0ee7`
   - `SPOTIFY_PLAYLIST_ID`: `https://open.spotify.com/playlist/12rwd7QxhciiOkEimw2Sav?si=sPPoIMPqQr-r6uhXFnCa3g`
   - `YTMUSIC_PLAYLIST_ID`: `PLd7k0zXVIOKuZE6w37l7hHWcJ20BpGhXj`
   - `SPOTIFY_REDIRECT_URI`: `https://3fa005f4-6983-4dd5-9e92-9606417872ae-00-375ctzyoxwck0.worf.replit.dev/callback`
   - `SPOTIFY_REFRESH_TOKEN`: `AQDBxIMcB1xfvzFvVTQjHt0Y342XrqpjY8GrflDqJcGdkf2dLI5kWmcYmZe4XSZwww-dicNvf7BMFTqAaqa0LYdaHtvgH7qKkOea13s2guFn5WZI2xIG2qoGkwrFa3-29ts`
   - `YTMUSIC_COOKIE`: 
     ```
     SOCS=CAAaBgiAqtjJBg; __Secure-YENID=12.YTE=MupJPZ3FrtB3tihqEPBoi_yQ-6lDCaMhcp1VRWe2ME4cLttbm6O6eGGc39bRE5OnY-xnH9NQF5orqLH5JhjtSEF7QSeXgxsIitzioqvbiaOFSOvqbik3AnqTcy6hdAN373_XLFzus2oy2eEaPv1letlqhAaR-tf_zutHS26IJAPelpodLW5FkGO7Dwv45u7f291Xd-hAR4pcbckwXa_N3drPO3bgJ7hs8zr3tF0Y5k7EyBhllAH1D5O6skvtojs6UP-gI1Yf4rI_Jw5nK1y9uI46LZZCzqNq2Wx5oFqcfaMX8CGWEkvS5joxqRQGxST8Yd2PmTjZUb6Qpb62rodpYg; YSC=ANTH7J0gu7Q; VISITOR_PRIVACY_METADATA=CgJJVBIhEh0SGwsMDg8QERITFBUWFxgZGhscHR4fICEiIyQlJiAd; __Secure-1PSIDTS=sidts-CjQBfl…fICEiIyQlJiAdYuACCt0CMTIuWVRFPU11cEpQWjNGcnRCM3RpaHFFUEJvaV95US02bERDYU1oY3AxVlJXZTJNRTRjTHR0Ym02TzZlR0djMzliUkU1T25ZLXhuSDlOUUY1b3JxTEg1SmhqdFNFRjdRU2VYZ3hzSWl0emlvcXZiaWFPRlNPdnFiaWszQW5xVGN5NmhkQU4zNzNfWExGenVzMm95MmVFYVB2MWxldGxxaEFhUi10Zl96dXRIUzI2SUpBUGVscG9kTFc1RmtHTzdEd3Y0NXU3ZjI5MVhkLWhBUjRwY2Jja3dYYV9OM2RyUE8zYmdKN2hzOHpyM3RGMFk1azdFeUJobGxBSDFENU82c2t2dG9qczZVUC1nSTFZZjRySV9KdzVuSzF5OXVJNDZMWlpDenFOcTJXeDVvRnFjZmFNWDhDR1dFa3ZTNWpveHFSUUd4U1Q4WWQyUG1UalpVYjZRcGI2MnJvZHBZZw==; PREF=repeat=NONE
     ```
   > **Suggerimento**: sostituisci questi valori con le tue credenziali per evitare che i token preconfigurati scadano o non abbiano accesso alle tue playlist.
3. Apri la sezione **Tools → Secrets** e, se vuoi usare le tue credenziali, sovrascrivi i valori di cui sopra:
   - `SPOTIFY_CLIENT_ID` e `SPOTIFY_CLIENT_SECRET`: presi dalla tua app su [Spotify for Developers](https://developer.spotify.com/dashboard/).
   - `SPOTIFY_REFRESH_TOKEN`: ottienilo con il tuo account (scope `playlist-read-private playlist-modify-public playlist-modify-private`).
   - `SPOTIFY_REDIRECT_URI`: lo stesso URI registrato nella dashboard Spotify. Puoi usare `http://localhost:8888/callback` in locale oppure l'URL del tuo Repl con `/callback` (es. `https://<il-tuo-nome>.<user>.repl.co/callback`).
   - `SPOTIFY_PLAYLIST_ID`: ID della playlist sorgente/destinazione su Spotify (solo la parte finale dell'URL o l'URI completo).
   - `YTMUSIC_COOKIE`: stringa di autenticazione `ytmusicapi` esportata dal tuo browser (header `cookie` completo dalla scheda YouTube Music).
   - `YTMUSIC_PLAYLIST_ID`: ID della playlist su YouTube Music (l'ID dopo `?list=` nell'URL).
   - `SYNC_DIRECTION` *(opzionale)*: `both` (default), `spotify_to_yt` oppure `yt_to_spotify` per limitare la direzione di sincronizzazione.
4. Installa le dipendenze con `pip install -r requirements.txt` (su Replit viene eseguito automaticamente al primo run).
5. Avvia lo script con `python sync_playlists.py`. Il log finale mostrerà quanti brani sono stati aggiunti su ciascuna piattaforma.

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
   - Non serve aggiungere `x-goog-authuser`: lo script imposta automaticamente l'account principale (`0`).
   - Assicurati che il cookie contenga i token `__Secure-3PSID` o `SAPISID`. Se mancano, ripeti l'estrazione dalla scheda *Network* di **music.youtube.com** (non `youtube.com`).
4. **Playlist ID**: apri la playlist su YouTube Music e copia l'ID dopo `?list=` nell'URL.

### Automatizzare i run su Replit
- Questo repository contiene un file `.replit` con `alwaysOn = true` per mantenere il Repl attivo di default.
- Puoi comunque aggiungere un **Scheduled task** (`.replit` → *Scheduled tasks*) che esegua `python sync_playlists.py` ogni pochi minuti se vuoi una cadenza specifica.
- In alternativa, usa il tab *Shell* e lancia `while true; do python sync_playlists.py; sleep 300; done` per avere un ciclo continuo (consuma le risorse del Repl attivo).

## Note importanti
- Assicurati che le playlist siano *tue* o che tu abbia i permessi per modificarle.
- Se un brano non viene trovato su una piattaforma, viene semplicemente ignorato nel ciclo successivo.
- Conserva i token e i cookie solo in ambienti sicuri (Secrets di Replit) per proteggere il tuo account.

## Risoluzione errori comuni
- **`SpotifyOauthError: invalid_grant` / HTTP 400 su `/api/token`**
  - Verifica che `SPOTIFY_REDIRECT_URI` sia identico a uno dei *Redirect URIs* salvati nella tua app Spotify (incluso l'URL del Repl se usato per l'OAuth).
  - Rigenera il `SPOTIFY_REFRESH_TOKEN` eseguendo `python spotify_refresh_token.py` e incolla il nuovo valore nelle Secrets del Repl.
  - Assicurati di aver autorizzato l'app con lo stesso account usato per la playlist e con gli scope elencati (`playlist-read-private playlist-modify-private playlist-modify-public`).
- **Errore di autenticazione YouTube Music / 401**
  - Controlla di aver incollato il cookie da `music.youtube.com` e non da `youtube.com`.
  - Verifica che il cookie contenga `__Secure-3PSID` o `SAPISID` (se mancano, estrai di nuovo l'header completo dalla richiesta `browse`).
  - Evita finestre in incognito: i cookie potrebbero essere incompleti o scadere subito.
- **`json.decoder.JSONDecodeError` su `ytmusicapi`**
  - Significa che `YTMUSIC_COOKIE` contiene un file/JSON (es. `browser.json`) invece del valore dell'header `cookie`.
  - Copia di nuovo l'header `cookie` completo dalla scheda *Network* di `music.youtube.com` e incollalo come singola stringa nella Secret `YTMUSIC_COOKIE` (non serve altro).
- **`Couldn't write token to cache at: .cache` su Spotify**
  - Ora la cache è disattivata nel codice, ma se vedi l'errore aggiorna il Repl con l'ultima versione oppure cancella eventuali permessi di sola-lettura sulla directory `.cache`.
