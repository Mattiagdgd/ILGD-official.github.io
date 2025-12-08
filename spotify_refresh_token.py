"""Utility per ottenere un refresh token Spotify via OAuth."""
from __future__ import annotations

import os

from spotipy.oauth2 import SpotifyOAuth

SCOPE = "playlist-read-private playlist-modify-private playlist-modify-public"

DEFAULT_VARS = {
    "SPOTIFY_CLIENT_ID": "4a2e9bd9c5bb4c05a0b05f1062ac7e70",
    "SPOTIFY_CLIENT_SECRET": "650e7d4a91cc4fae896bc3f0b0ff0ee7",
    "SPOTIFY_REDIRECT_URI": "https://3fa005f4-6983-4dd5-9e92-9606417872ae-00-375ctzyoxwck0.worf.replit.dev/callback",
}


def _env_or_input(name: str, prompt: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    value = input(prompt).strip()
    if not value:
        raise SystemExit(f"Valore mancante per {name}")
    return value


def main() -> None:
    for key, value in DEFAULT_VARS.items():
        os.environ.setdefault(key, value)

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
