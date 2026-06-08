from pathlib import Path

import yaml

from src.models import Event
from src.sources import ctftime, mlh
from src.notifiers import discord


def load_config() -> dict:
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


def collect_events(config: dict) -> list[Event]:
    events: list[Event] = []
    sources = config.get("sources", {})

    if sources.get("ctftime"):
        print("Fetching from CTFtime...")
        try:
            events.extend(ctftime.fetch_events(config))
        except Exception as e:
            print(f"CTFtime fetch failed: {e}")

    if sources.get("mlh"):
        print("Fetching from MLH...")
        try:
            events.extend(mlh.fetch_events(config))
        except Exception as e:
            print(f"MLH fetch failed: {e}")

    # Deduplicate by name + start date
    seen = set()
    unique = []
    for event in events:
        key = (event.name.lower(), event.start.date())
        if key not in seen:
            seen.add(key)
            unique.append(event)

    # Sort by start date
    unique.sort(key=lambda e: e.start)
    return unique


def main():
    config = load_config()
    events = collect_events(config)

    print(f"Found {len(events)} events")
    for event in events:
        print(f"  - {event.name} ({event.location}, {event.start:%b %d})")

    discord.send_events(events)
    print("Notifications sent!")


if __name__ == "__main__":
    main()
