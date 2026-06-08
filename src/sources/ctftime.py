import httpx
from datetime import datetime, timedelta, timezone
from math import radians, cos, sin, asin, sqrt

from src.models import Event


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in km between two lat/lon points."""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * 6371 * asin(sqrt(a))


def fetch_events(config: dict) -> list[Event]:
    loc = config["location"]
    days_ahead = config["notify"]["days_ahead"]

    now = datetime.now(timezone.utc)
    start = int(now.timestamp())
    end = int((now + timedelta(days=days_ahead)).timestamp())

    resp = httpx.get(
        "https://ctftime.org/api/v1/events/",
        params={"limit": 100, "start": start, "finish": end},
        headers={"User-Agent": "pingme/0.1"},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    events = []
    for item in data:
        online = item.get("onsite", False) is False
        event_loc = item.get("location", "")

        if online:
            if not loc.get("include_online", True):
                continue
        else:
            # Try to filter by country first
            restrictions = item.get("restrictions", "")
            if restrictions and "US" not in restrictions.upper():
                pass  # still check coordinates if available

            # If location has coordinates, filter by distance
            lat = item.get("lat")
            lon = item.get("lng")
            if lat and lon:
                dist = haversine(loc["lat"], loc["lon"], float(lat), float(lon))
                if dist > loc["radius_km"]:
                    continue
            elif not _location_matches_region(event_loc):
                continue

        events.append(Event(
            name=item["title"],
            url=item.get("url") or item.get("ctftime_url", ""),
            start=datetime.fromisoformat(item["start"]),
            end=datetime.fromisoformat(item["finish"]),
            location=event_loc or ("Online" if online else "Unknown"),
            online=online,
            source="CTFtime",
            description=item.get("description", "")[:200],
            format=item.get("format", ""),
        ))

    return events


def _location_matches_region(location: str) -> bool:
    """Fuzzy check if location string mentions mid-Atlantic US region."""
    keywords = [
        "baltimore", "maryland", "md", "washington", "dc", "virginia",
        "va", "philadelphia", "pennsylvania", "pa", "delaware", "de",
        "new jersey", "nj",
    ]
    loc_lower = location.lower()
    return any(kw in loc_lower for kw in keywords)
