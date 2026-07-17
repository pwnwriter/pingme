from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class Event:
    name: str
    url: str
    start: datetime
    end: datetime
    location: str
    online: bool
    source: str
    description: str = ""
    format: str = ""

    def _days_until(self) -> int:
        now = datetime.now(timezone.utc)
        return max(0, (self.start.replace(tzinfo=timezone.utc) - now).days)

    def _urgency_color(self) -> int:
        days = self._days_until()
        if days <= 1:
            return 0xED4245  # Discord red \u2014 urgent
        if days <= 5:
            return 0xFEE75C  # Discord yellow \u2014 coming up
        return 0x5865F2      # Discord blurple \u2014 later

    def _status_emoji(self) -> str:
        days = self._days_until()
        if days == 0:
            return "\U0001F534"  # red circle
        if days == 1:
            return "\U0001F7E0"  # orange circle
        if days <= 5:
            return "\U0001F7E1"  # yellow circle
        return "\U0001F535"      # blue circle

    def embed_dict(self) -> dict:
        days = self._days_until()
        ts = int(self.start.replace(tzinfo=timezone.utc).timestamp())
        ts_end = int(self.end.replace(tzinfo=timezone.utc).timestamp())

        if days == 0:
            when = "**Happening today**"
        elif days == 1:
            when = "**Starts tomorrow**"
        else:
            when = f"**Starts in {days} days**"

        desc_lines = [when]
        if self.description:
            clean = self.description[:200].strip()
            if clean:
                desc_lines.append(f"> {clean}")

        where = "\U0001F310 Remote" if self.online else f"\U0001F4CD {self.location}"
        fmt = self.format.title() if self.format else "\u2014"

        return {
            "title": f"{self._status_emoji()} {self.name}",
            "url": self.url,
            "description": "\n".join(desc_lines),
            "color": self._urgency_color(),
            "fields": [
                {"name": "Where", "value": where, "inline": True},
                {"name": "Format", "value": fmt, "inline": True},
                {"name": "Source", "value": self.source, "inline": True},
                {"name": "Starts", "value": f"<t:{ts}:f>", "inline": True},
                {"name": "Ends", "value": f"<t:{ts_end}:f>", "inline": True},
                {"name": "Starts in", "value": f"<t:{ts}:R>", "inline": True},
            ],
            "footer": {"text": "pingme"},
        }
