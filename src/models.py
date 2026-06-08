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
            return 0xFF0033  # red alert
        if days <= 5:
            return 0x00FF41  # matrix green
        return 0x0D0D0D      # dark

    def embed_dict(self) -> dict:
        days = self._days_until()
        ts = int(self.start.replace(tzinfo=timezone.utc).timestamp())
        ts_end = int(self.end.replace(tzinfo=timezone.utc).timestamp())

        if days == 0:
            tag = "[!] LIVE NOW"
        elif days == 1:
            tag = "[!] T-1 DAY"
        elif days <= 5:
            tag = f"[*] T-{days} DAYS"
        else:
            tag = f"[ ] T-{days} DAYS"

        if self.online:
            loc = "`REMOTE`"
        else:
            loc = f"`{self.location.upper()}`"

        desc_lines = []
        if self.description:
            clean = self.description[:120].strip()
            if clean:
                desc_lines.append(f"```\n{clean}\n```")

        desc_lines.append(f"**START** \u2192 <t:{ts}:F>")
        desc_lines.append(f"**END** \u2192 <t:{ts_end}:F>")
        desc_lines.append(f"**ETA** \u2192 <t:{ts}:R>")

        mode = "ONSITE" if not self.online else "REMOTE"
        fmt = self.format.upper() if self.format else "N/A"

        return {
            "title": f"{tag} // {self.name}",
            "url": self.url,
            "description": "\n".join(desc_lines),
            "color": self._urgency_color(),
            "fields": [
                {"name": "> LOC", "value": loc, "inline": True},
                {"name": "> MODE", "value": f"`{mode}`", "inline": True},
                {"name": "> TYPE", "value": f"`{fmt}`", "inline": True},
                {"name": "> SRC", "value": f"`{self.source.upper()}`", "inline": True},
            ],
            "footer": {"text": f"// pingme v0.1 | {self.source}"},
        }
