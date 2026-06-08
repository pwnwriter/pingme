from dataclasses import dataclass
from datetime import datetime


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

    def embed_dict(self) -> dict:
        fields = [
            {"name": "Date", "value": f"{self.start:%b %d} - {self.end:%b %d, %Y}", "inline": True},
            {"name": "Location", "value": self.location if not self.online else "Online", "inline": True},
            {"name": "Source", "value": self.source, "inline": True},
        ]
        if self.format:
            fields.append({"name": "Format", "value": self.format, "inline": True})

        return {
            "title": self.name,
            "url": self.url,
            "description": self.description[:200] if self.description else "",
            "fields": fields,
            "color": 0x5865F2,
        }
