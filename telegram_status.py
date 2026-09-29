import asyncio
import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request

from telethon import TelegramClient
from telethon.errors import AboutTooLongError
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest

# Text shown when nothing is playing (edit as you like)
IDLE = "🎧 в наушниках тишина"
PREFIX = "🎧 слушает: "
# Telegram "About" limit: usually 70 chars, Premium has more
LIMIT = int(os.environ.get("TG_BIO_LIMIT", "70"))


def spotify_token() -> str:
    cid = os.environ["SPOTIFY_CLIENT_ID"]
    secret = os.environ["SPOTIFY_CLIENT_SECRET"]
    refresh = os.environ["SPOTIFY_REFRESH_TOKEN"]
    basic = base64.b64encode(f"{cid}:{secret}".encode()).decode()
    data = urllib.parse.urlencode(
        {"grant_type": "refresh_token", "refresh_token": refresh}
    ).encode()
    req = urllib.request.Request(
        "https://accounts.spotify.com/api/token",
        data=data,
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    with urllib.request.urlopen(req) as r:
        return json.load(r)["access_token"]


def now_playing(token: str):
    req = urllib.request.Request(
        "https://api.spotify.com/v1/me/player/currently-playing",
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(req) as r:
            if r.status != 200:
                return None
            data = json.load(r)
    except urllib.error.HTTPError:
        return None
    if not data.get("is_playing") or data.get("currently_playing_type") != "track":
        return None
    item = data.get("item") or {}
    artists = item.get("artists") or []
    artist = artists[0]["name"] if artists else ""
    title = item.get("name", "")
    if not title:
        return None
    return f"{artist} — {title}" if artist else title


def build_bio(track, limit: int) -> str:
    if not track:
        return IDLE
    text = PREFIX + track
    if len(text) > limit:
        text = text[: limit - 1].rstrip() + "…"
    return text


async def main():
    track = now_playing(spotify_token())
    async with TelegramClient(
        StringSession(os.environ["TG_SESSION"]),
        int(os.environ["TG_API_ID"]),
        os.environ["TG_API_HASH"],
    ) as client:
        current = (await client(GetFullUserRequest("me"))).full_user.about or ""
        bio = build_bio(track, LIMIT)
        if current == bio:
            print("Bio unchanged, nothing to do.")
            return
        try:
            await client(UpdateProfileRequest(about=bio))
        except AboutTooLongError:
            bio = build_bio(track, LIMIT - 5)
            await client(UpdateProfileRequest(about=bio))
        print(f"Bio set: {bio}")


asyncio.run(main())
