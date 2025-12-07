"""
Script per sincronizzare automaticamente le playlist tra Spotify e YouTube Music.
Pensato per essere eseguito su Replit con variabili d'ambiente.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple

from spotipy import Spotify
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
    if not value:
        raise RuntimeError(f"Variabile d'ambiente mancante: {name}")
    return value


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
