"""Utility per ottenere un refresh token Spotify via OAuth."""
from __future__ import annotations

import os

from spotipy.oauth2 import SpotifyOAuth

SCOPE = "playlist-read-private playlist-modify-private playlist-modify-public"


def _env_or_input(name: str, prompt: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    value = input(prompt).strip()
    if not value:
        raise SystemExit(f"Valore mancante per {name}")
    return value


def main() -> None:
    client_id = _env_or_input("SPOTIFY_CLIENT_ID", "Spotify Client ID: ")
    client_secret = _env_or_input("SPOTIFY_CLIENT_SECRET", "Spotify Client Secret: ")
    redirect_uri = _env_or_input(
        "SPOTIFY_REDIRECT_URI", "Redirect URI registrato (es. http://localhost:8888/callback): "
    )

    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=SCOPE,
        cache_path=".cache-spotify-token",
    )

    token_info = auth_manager.get_access_token(as_dict=True)
    refresh_token = token_info.get("refresh_token")
    if not refresh_token:
        raise SystemExit("Impossibile ricavare il refresh token. Verifica scope e redirect URI.")

    print("\n==== REFRESH TOKEN SPOTIFY ====")
    print(refresh_token)
    print("==============================")
    print("Salvalo come SPOTIFY_REFRESH_TOKEN nelle tue Secrets.")

    # Pulisce il cache file per evitare di lasciarlo nel repository.
    cache_file = ".cache-spotify-token"
    if os.path.exists(cache_file):
        os.remove(cache_file)


if __name__ == "__main__":
    main()
