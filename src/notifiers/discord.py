import os
from datetime import datetime, timezone

import httpx

from src.models import Event

API = "https://discord.com/api/v10"


def _headers() -> dict:
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_BOT_TOKEN environment variable not set")
    return {"Authorization": f"Bot {token}"}


def _channel_id() -> str:
    channel_id = os.environ.get("DISCORD_CHANNEL_ID")
    if not channel_id:
        raise RuntimeError("DISCORD_CHANNEL_ID environment variable not set")
    return channel_id


def _get_bot_id() -> str:
    resp = httpx.get(f"{API}/users/@me", headers=_headers(), timeout=15)
    resp.raise_for_status()
    return resp.json()["id"]


def _purge_old_messages(channel_id: str, bot_id: str) -> None:
    try:
        resp = httpx.get(
            f"{API}/channels/{channel_id}/messages",
            headers=_headers(),
            params={"limit": 50},
            timeout=15,
        )
        resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        print(f"Could not read message history (missing permissions?): {e.response.status_code}")
        return

    for msg in resp.json():
        if msg["author"]["id"] == bot_id:
            try:
                httpx.delete(
                    f"{API}/channels/{channel_id}/messages/{msg['id']}",
                    headers=_headers(),
                    timeout=15,
                )
            except httpx.HTTPStatusError:
                pass


def _send_message(channel_id: str, payload: dict) -> None:
    resp = httpx.post(
        f"{API}/channels/{channel_id}/messages",
        headers=_headers(),
        json=payload,
        timeout=15,
    )
    resp.raise_for_status()


def send_events(events: list[Event]) -> None:
    channel_id = _channel_id()
    bot_id = _get_bot_id()

    _purge_old_messages(channel_id, bot_id)

    now = datetime.now(timezone.utc)
    ts = f"<t:{int(now.timestamp())}:f>"

    if not events:
        _send_message(channel_id, {
            "embeds": [{
                "title": "🌙 No Upcoming Events",
                "description": (
                    "Nothing found in range right now — check back soon.\n\n"
                    "**Next scan:** Mon/Thu, 9:00 AM EST"
                ),
                "color": 0x5865F2,
                "footer": {"text": f"Last checked {ts}"},
            }],
        })
        return

    onsite = [e for e in events if not e.online]
    online = [e for e in events if e.online]

    # Header
    plural = "s" if len(events) != 1 else ""
    _send_message(channel_id, {
        "embeds": [{
            "title": "📡 Event Scan",
            "description": f"Found **{len(events)}** upcoming event{plural} in the next 21 days.",
            "color": 0x57F287,
            "fields": [
                {"name": "📍 Onsite", "value": str(len(onsite)), "inline": True},
                {"name": "🌐 Remote", "value": str(len(online)), "inline": True},
            ],
            "footer": {"text": f"Scanned {ts}"},
        }],
    })

    # Send onsite first, then online
    all_events = onsite + online
    for i in range(0, len(all_events), 5):
        batch = all_events[i:i + 5]
        _send_message(channel_id, {
            "embeds": [e.embed_dict() for e in batch],
        })
