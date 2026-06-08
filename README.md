# pingme

Scans for upcoming hackathons and CTF competitions near you and sends Discord notifications. Runs on GitHub Actions — no server needed.

## Why

I missed more than 10 CTF competitions just because I didn't know they were happening nearby. By the time I'd find out, registration was closed or the event was already over. Built this so I'd never miss one again.

## Setup

1. Fork this repo
2. Edit `config.yaml` with your location
3. Add `DISCORD_WEBHOOK_URL` as a GitHub Actions secret
4. Run from Actions tab or wait for the daily cron

<details>
<summary>Discord webhook setup</summary>

1. Go to your Discord server → **Server Settings** → **Integrations** → **Webhooks**
2. Create a new webhook, pick your channel, copy the URL
3. In your fork → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**
   - Name: `DISCORD_WEBHOOK_URL`
   - Value: your webhook URL

</details>

<details>
<summary>Configuration</summary>

```yaml
location:
  city: "Baltimore"
  lat: 39.2904
  lon: -76.6122
  radius_km: 200
  include_online: true

sources:
  ctftime: true
  mlh: true

notify:
  days_ahead: 21
```

| Field | Description |
|-------|-------------|
| `location.lat` / `location.lon` | Coordinates for distance filtering |
| `location.radius_km` | How far to search (km) |
| `location.include_online` | Include online/virtual events |
| `sources.ctftime` | Enable CTFtime scanning |
| `sources.mlh` | Enable MLH scanning |
| `notify.days_ahead` | How far ahead to look for events |

</details>

<details>
<summary>Run locally</summary>

```bash
DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..." uv run main.py
```

</details>

## Sources

- [CTFtime](https://ctftime.org) — CTF competitions
- [MLH](https://mlh.io) — Hackathons

## Contributing

PRs welcome — especially new event sources. To add one, create a file in `sources/` that exports a `fetch_events(config) -> list[Event]` function and enable it in `config.yaml`.

Bug fixes, better parsing, and new notifiers (Slack, Telegram, etc.) are all fair game too.


## License
 Licensed under the [**`MIT LICENSE`**](/LICENSE) 

 
<p align="center"><img src="https://raw.githubusercontent.com/catppuccin/catppuccin/main/assets/footers/gray0_ctp_on_line.svg?sanitize=true" /></p>
<p align="center">Copyright &copy; 2026 - present <a href="https://pwnwriter.me" target="_blank"> pwnwriter me </a> ☘️</p> 
