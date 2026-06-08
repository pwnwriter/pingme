from dataclasses import dataclass
from datetime import datetime, timezone

COLORS = {
    "CTFtime": 0xE74C3C,   # red
    "MLH": 0x2ECC71,       # green
}

SOURCE_ICONS = {
    "CTFtime": "https://ctftime.org/static/images/ct/favicon-32x32.png",
    "MLH": "https://static.mlh.io/brand-assets/logo/official/mlh-logo-color.png",
}


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
        return (self.start.replace(tzinfo=timezone.utc) - now).days

    def embed_dict(self) -> dict:
        days = self._days_until()
        if days <= 1:
            urgency = "TOMORROW"
        elif days <= 3:
            urgency = f"in {days} days"
        else:
            urgency = f"in {days} days"

        time_str = f"<t:{int(self.start.replace(tzinfo=timezone.utc).timestamp())}:F>"
        time_relative = f"<t:{int(self.start.replace(tzinfo=timezone.utc).timestamp())}:R>"

        location_val = self.location if not self.online else "Online"

        lines = []
        if self.description:
            desc = self.description[:150].strip()
            if desc:
                lines.append(f"*{desc}*")
        lines.append("")
        lines.append(f"**Starts:** {time_str} ({time_relative})")
        lines.append(f"**Location:** {location_val}")
        if self.format:
            lines.append(f"**Format:** {self.format}")

        color = COLORS.get(self.source, 0x5865F2)
        badge = "ONSITE" if not self.online else "ONLINE"

        embed = {
            "title": f"{self.name}",
            "url": self.url,
            "description": "\n".join(lines),
            "color": color,
            "footer": {
                "text": f"{self.source} | {badge}",
                "icon_url": SOURCE_ICONS.get(self.source, ""),
            },
        }

        if days <= 1:
            embed["title"] = f"[TOMORROW] {self.name}"
        elif days <= 3:
            embed["title"] = f"[SOON] {self.name}"

        return embed
