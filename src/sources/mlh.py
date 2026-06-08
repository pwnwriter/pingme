import httpx
from datetime import datetime, timedelta, timezone
from selectolax.parser import HTMLParser

from src.models import Event
from src.sources.ctftime import haversine


MLH_URL = "https://www.mlh.com/seasons/2026/events"


def fetch_events(config: dict) -> list[Event]:
    loc = config["location"]
    days_ahead = config["notify"]["days_ahead"]
    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(days=days_ahead)

    resp = httpx.get(MLH_URL, headers={"User-Agent": "pingme/0.1"}, timeout=30)
    resp.raise_for_status()

    tree = HTMLParser(resp.text)
    events = []

    for card in tree.css(".event"):
        name_el = card.css_first(".event-name")
        if not name_el:
            continue

        name = name_el.text(strip=True)
        link_el = card.css_first("a[href]")
        url = link_el.attributes.get("href", "") if link_el else ""

        date_el = card.css_first(".event-date")
        location_el = card.css_first(".event-location")

        event_loc = location_el.text(strip=True) if location_el else ""
        date_text = date_el.text(strip=True) if date_el else ""

        # Parse date — MLH uses formats like "Jun 13th - 15th, 2025"
        start, end = _parse_mlh_date(date_text)
        if not start or start > cutoff or start < now:
            continue

        online = "digital" in event_loc.lower() or "virtual" in event_loc.lower()

        if not online:
            if not _is_nearby(event_loc, loc):
                continue

        if online and not loc.get("include_online", True):
            continue

        events.append(Event(
            name=name,
            url=url,
            start=start,
            end=end or start,
            location=event_loc or ("Online" if online else "Unknown"),
            online=online,
            source="MLH",
            format="Hackathon",
        ))

    return events


def _is_nearby(event_loc: str, loc: dict) -> bool:
    """Check if event location is in the configured region."""
    keywords = [
        "baltimore", "maryland", "md", "washington", "dc", "virginia",
        "va", "philadelphia", "pennsylvania", "pa", "delaware", "de",
        "new jersey", "nj", "annapolis",
    ]
    loc_lower = event_loc.lower()
    return any(kw in loc_lower for kw in keywords)


def _parse_mlh_date(text: str) -> tuple[datetime | None, datetime | None]:
    """Best-effort parse of MLH date strings."""
    import re

    text = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", text)
    # "Jun 13 - 15, 2025" or "Jun 13 - Jul 15, 2025"
    try:
        if " - " in text:
            parts = text.split(" - ")
            end_part = parts[1].strip()
            start_part = parts[0].strip()

            # If end has year, extract it
            year_match = re.search(r"\d{4}", end_part)
            year = int(year_match.group()) if year_match else datetime.now().year

            # Parse start
            start = _parse_date_part(start_part, year)
            end = _parse_date_part(end_part, year)
            return start, end
        else:
            year = datetime.now().year
            return _parse_date_part(text, year), None
    except (ValueError, IndexError):
        return None, None


def _parse_date_part(text: str, year: int) -> datetime | None:
    import re

    text = re.sub(r",?\s*\d{4}", "", text).strip()
    for fmt in ("%b %d", "%B %d"):
        try:
            dt = datetime.strptime(text, fmt)
            return dt.replace(year=year, tzinfo=timezone.utc)
        except ValueError:
            continue

    # Try just day number (e.g., "15" from "Jun 13 - 15")
    try:
        day = int(re.search(r"\d+", text).group())
        return datetime(year, 1, day, tzinfo=timezone.utc)
    except (ValueError, AttributeError):
        return None
