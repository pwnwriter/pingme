import os
import httpx

from models import Event


def send_events(events: list[Event]) -> None:
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        raise RuntimeError("DISCORD_WEBHOOK_URL environment variable not set")

    if not events:
        _send_payload(webhook_url, {
            "content": "No upcoming hackathons or CTFs found nearby this week.",
        })
        return

    # Discord allows up to 10 embeds per message
    for i in range(0, len(events), 10):
        batch = events[i:i + 10]
        payload = {
            "content": f"**Found {len(events)} upcoming events near Baltimore!**" if i == 0 else "",
            "embeds": [e.embed_dict() for e in batch],
        }
        _send_payload(webhook_url, payload)


def _send_payload(webhook_url: str, payload: dict) -> None:
    resp = httpx.post(webhook_url, json=payload, timeout=15)
    resp.raise_for_status()
