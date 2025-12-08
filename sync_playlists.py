"""
Script per sincronizzare automaticamente le playlist tra Spotify e YouTube Music.
Pensato per essere eseguito su Replit con variabili d'ambiente.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth, SpotifyOauthError
from spotipy.oauth2 import SpotifyOAuth
from ytmusicapi import YTMusic


@dataclass
class Track:
    title: str
    artist: str

    @property
    def search_query(self) -> str:
        return f"{self.title} {self.artist}".strip()


class SpotifyClient:
    def __init__(self, client_id: str, client_secret: str, refresh_token: str, redirect_uri: str):
        self.auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope="playlist-read-private playlist-modify-private playlist-modify-public",
            cache_handler=None,  # evita tentativi di scrittura su .cache in ambienti read-only
        )
        try:
            self.auth_manager.refresh_access_token(refresh_token)
        except SpotifyOauthError as exc:  # pragma: no cover - network/OAuth path
            raise SystemExit(
                "Refresh token Spotify non valido. Rigenera SPOTIFY_REFRESH_TOKEN con "
                "spotify_refresh_token.py e assicurati che SPOTIFY_REDIRECT_URI combaci con quello "
                "registrato nell'app Spotify."
            ) from exc
            cache_path=None,
        )
        self.auth_manager.refresh_access_token(refresh_token)
        self.api = Spotify(auth_manager=self.auth_manager)

    def get_playlist_tracks(self, playlist_id: str) -> List[Track]:
        tracks: List[Track] = []
        results = self.api.playlist_tracks(playlist_id)
        while True:
            tracks.extend(
                Track(item["track"]["name"], item["track"]["artists"][0]["name"])  # type: ignore[index]
                for item in results.get("items", [])
                if item and item.get("track")
            )
            if results.get("next"):
                results = self.api.next(results)
            else:
                break
        return tracks

    def find_track(self, query: str) -> Optional[str]:
        results = self.api.search(q=query, type="track", limit=1)
        items = results.get("tracks", {}).get("items", [])  # type: ignore[union-attr]
        return items[0]["uri"] if items else None

    def add_tracks(self, playlist_id: str, track_uris: Iterable[str]) -> None:
        batch: List[str] = []
        for uri in track_uris:
            batch.append(uri)
            if len(batch) == 100:
                self.api.playlist_add_items(playlist_id, batch)
                batch.clear()
        if batch:
            self.api.playlist_add_items(playlist_id, batch)


class YTMusicClient:
    def __init__(self, cookie: str):
        stripped = cookie.strip()
        if stripped.endswith(".json") or ("{" in stripped and "}" in stripped):
            raise SystemExit(
                "YTMUSIC_COOKIE deve essere l'header `cookie` copiato da music.youtube.com, non un file "
                "JSON (es. browser.json) né il contenuto JSON di ytmusicapi. Incolla il valore unico di "
                "`cookie` dalla scheda Network."
            )

        if "__Secure-3PSID" not in cookie and "SAPISID" not in cookie:
            raise SystemExit(
                "YTMUSIC_COOKIE non valido: copia l'header `cookie` completo dalla scheda "
                "Network di music.youtube.com (non youtube.com) mentre sei loggato, includendo i token "
                "__Secure-3PSID/SAPISID."
            )

        headers = {
            "cookie": cookie,
            # browser-like UA to avoid stricter validation on some Replit hosts
            "user-agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            # imposto automaticamente l'account principale per evitare di dover passare x-goog-authuser
            "x-goog-authuser": "0",
            "x-origin": "https://music.youtube.com",
        }
        try:
            self.api = YTMusic(auth=headers)
        except Exception as exc:  # pragma: no cover - network/OAuth path
            raise SystemExit(
                "Autenticazione YouTube Music fallita: verifica di aver incollato il cookie da "
                "music.youtube.com (non da youtube.com) e senza andare in scadenza."
            ) from exc
        self.api = YTMusic(auth=cookie)

    def get_playlist_tracks(self, playlist_id: str) -> List[Track]:
        playlist = self.api.get_playlist(playlist_id, limit=5000)
        tracks = playlist.get("tracks", []) or []
        return [
            Track(item.get("title", ""), (item.get("artists") or [{}])[0].get("name", ""))
            for item in tracks
        ]

    def find_track(self, query: str) -> Optional[str]:
        search_results = self.api.search(query, filter="songs", limit=1)
        return search_results[0].get("videoId") if search_results else None

    def add_tracks(self, playlist_id: str, video_ids: Iterable[str]) -> None:
        to_add: List[str] = []
        for video_id in video_ids:
            to_add.append(video_id)
            if len(to_add) == 99:
                self.api.add_playlist_items(playlist_id, to_add)
                to_add.clear()
        if to_add:
            self.api.add_playlist_items(playlist_id, to_add)


def _get_env(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value

    default_value = DEFAULT_VARS.get(name)
    if default_value:
        print(f"{name} non trovato nelle variabili d'ambiente: uso il valore preconfigurato.")
        return default_value

    raise RuntimeError(f"Variabile d'ambiente mancante: {name}")


def _collect_missing(target_tracks: List[Track], source_tracks: List[Track]) -> Tuple[List[Track], set[str]]:
    target_keys = {t.search_query.lower() for t in target_tracks}
    missing = [t for t in source_tracks if t.search_query.lower() not in target_keys]
    return missing, target_keys


def sync_spotify_to_ytmusic(sp_client: SpotifyClient, yt_client: YTMusicClient, spotify_playlist_id: str, ytmusic_playlist_id: str) -> int:
    spotify_tracks = sp_client.get_playlist_tracks(spotify_playlist_id)
    yt_tracks = yt_client.get_playlist_tracks(ytmusic_playlist_id)
    missing, _ = _collect_missing(yt_tracks, spotify_tracks)

    video_ids = []
    for track in missing:
        video_id = yt_client.find_track(track.search_query)
        if video_id:
            video_ids.append(video_id)
    yt_client.add_tracks(ytmusic_playlist_id, video_ids)
    return len(video_ids)


def sync_ytmusic_to_spotify(sp_client: SpotifyClient, yt_client: YTMusicClient, spotify_playlist_id: str, ytmusic_playlist_id: str) -> int:
    yt_tracks = yt_client.get_playlist_tracks(ytmusic_playlist_id)
    sp_tracks = sp_client.get_playlist_tracks(spotify_playlist_id)
    missing, _ = _collect_missing(sp_tracks, yt_tracks)

    uris = []
    for track in missing:
        uri = sp_client.find_track(track.search_query)
        if uri:
            uris.append(uri)
    sp_client.add_tracks(spotify_playlist_id, uris)
    return len(uris)


def main() -> None:
    direction = os.getenv("SYNC_DIRECTION", "both").lower()
    spotify_playlist_id = _get_env("SPOTIFY_PLAYLIST_ID")
    ytmusic_playlist_id = _get_env("YTMUSIC_PLAYLIST_ID")

    sp_client = SpotifyClient(
        client_id=_get_env("SPOTIFY_CLIENT_ID"),
        client_secret=_get_env("SPOTIFY_CLIENT_SECRET"),
        refresh_token=_get_env("SPOTIFY_REFRESH_TOKEN"),
        redirect_uri=_get_env("SPOTIFY_REDIRECT_URI"),
    )
    yt_client = YTMusicClient(cookie=_get_env("YTMUSIC_COOKIE"))

    added_to_yt = added_to_sp = 0

    if direction in {"spotify_to_yt", "both"}:
        added_to_yt = sync_spotify_to_ytmusic(sp_client, yt_client, spotify_playlist_id, ytmusic_playlist_id)
    if direction in {"yt_to_spotify", "both"}:
        added_to_sp = sync_ytmusic_to_spotify(sp_client, yt_client, spotify_playlist_id, ytmusic_playlist_id)

    print(f"Aggiunti {added_to_yt} brani su YouTube Music e {added_to_sp} su Spotify.")


if __name__ == "__main__":
    main()
DEFAULT_VARS = {
    "SPOTIFY_CLIENT_ID": "4a2e9bd9c5bb4c05a0b05f1062ac7e70",
    "SPOTIFY_CLIENT_SECRET": "650e7d4a91cc4fae896bc3f0b0ff0ee7",
    "SPOTIFY_PLAYLIST_ID": "https://open.spotify.com/playlist/12rwd7QxhciiOkEimw2Sav?si=sPPoIMPqQr-r6uhXFnCa3g",
    "YTMUSIC_PLAYLIST_ID": "PLd7k0zXVIOKuZE6w37l7hHWcJ20BpGhXj",
    "SPOTIFY_REDIRECT_URI": "https://3fa005f4-6983-4dd5-9e92-9606417872ae-00-375ctzyoxwck0.worf.replit.dev/callback",
    "SPOTIFY_REFRESH_TOKEN": "AQDBxIMcB1xfvzFvVTQjHt0Y342XrqpjY8GrflDqJcGdkf2dLI5kWmcYmZe4XSZwww-dicNvf7BMFTqAaqa0LYdaHtvgH7qKkOea13s2guFn5WZI2xIG2qoGkwrFa3-29ts",
    "YTMUSIC_COOKIE": "SOCS=CAAaBgiAqtjJBg; __Secure-YENID=12.YTE=MupJPZ3FrtB3tihqEPBoi_yQ-6lDCaMhcp1VRWe2ME4cLttbm6O6eGGc39bRE5OnY-xnH9NQF5orqLH5JhjtSEF7QSeXgxsIitzioqvbiaOFSOvqbik3AnqTcy6hdAN373_XLFzus2oy2eEaPv1letlqhAaR-tf_zutHS26IJAPelpodLW5FkGO7Dwv45u7f291Xd-hAR4pcbckwXa_N3drPO3bgJ7hs8zr3tF0Y5k7EyBhllAH1D5O6skvtojs6UP-gI1Yf4rI_Jw5nK1y9uI46LZZCzqNq2Wx5oFqcfaMX8CGWEkvS5joxqRQGxST8Yd2PmTjZUb6Qpb62rodpYg; YSC=ANTH7J0gu7Q; VISITOR_PRIVACY_METADATA=CgJJVBIhEh0SGwsMDg8QERITFBUWFxgZGhscHR4fICEiIyQlJiAd; __Secure-1PSIDTS=sidts-CjQBfl…fICEiIyQlJiAdYuACCt0CMTIuWVRFPU11cEpQWjNGcnRCM3RpaHFFUEJvaV95US02bERDYU1oY3AxVlJXZTJNRTRjTHR0Ym02TzZlR0djMzliUkU1T25ZLXhuSDlOUUY1b3JxTEg1SmhqdFNFRjdRU2VYZ3hzSWl0emlvcXZiaWFPRlNPdnFiaWszQW5xVGN5NmhkQU4zNzNfWExGenVzMm95MmVFYVB2MWxldGxxaEFhUi10Zl96dXRIUzI2SUpBUGVscG9kTFc1RmtHTzdEd3Y0NXU3ZjI5MVhkLWhBUjRwY2Jja3dYYV9OM2RyUE8zYmdKN2hzOHpyM3RGMFk1azdFeUJobGxBSDFENU82c2t2dG9qczZVUC1nSTFZZjRySV9KdzVuSzF5OXVJNDZMWlpDenFOcTJXeDVvRnFjZmFNWDhDR1dFa3ZTNWpveHFSUUd4U1Q4WWQyUG1UalpVYjZRcGI2MnJvZHBZZw==; PREF=repeat=NONE",
}

