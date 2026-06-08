
# pingme

***Scans for upcoming hackathons and CTF competitions near you and sends Discord notifications. Runs on GitHub Actions — no server needed***

<img width="368" height="290" alt="Screenshot 2026-06-08 at 12 51 26 AM" src="https://github.com/user-attachments/assets/e0a3467c-087b-4013-b542-3f00a6c31fee" />


## Why

I missed more than 10 CTF competitions just because I didn't know they were happening nearby. By the time I'd find out, registration was closed or the event was already over. Built this so I'd never miss one again.

## Setup

1. Fork this repo
2. Edit `config.yaml` with your location
3. Add `DISCORD_BOT_TOKEN` and `DISCORD_CHANNEL_ID` as GitHub Actions secrets
4. Run from the Actions tab or wait for the next scheduled scan (Monday & Thursday, 9am EST)

<details>
<summary>Discord bot setup</summary>

> Full reference: [Discord Developer Docs — Getting Started](https://discord.com/developers/docs/getting-started)

**Create the bot:**

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications) → **New Application**
2. Go to **Bot** → click **Reset Token** → copy the token (you'll only see it once)
3. Under **Privileged Gateway Intents**, enable **Message Content Intent**

**Invite it to your server:**

4. Go to **OAuth2** → **URL Generator**
5. Scope: `bot`
6. Permissions: `Send Messages`, `Manage Messages`, `Read Message History`, `View Channels`
7. Open the generated URL → select your server → **Authorize**

**Get the channel ID:**

8. In Discord → **User Settings** → **App Settings** → **Advanced** → enable **Developer Mode**
9. Right-click the channel you want notifications in → **Copy Channel ID**

**Add secrets to GitHub:**

10. In your fork → **Settings** → **Secrets and variables** → **Actions** → add two secrets:
    - `DISCORD_BOT_TOKEN` — your bot token
    - `DISCORD_CHANNEL_ID` — the channel ID

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
DISCORD_BOT_TOKEN="your-token" DISCORD_CHANNEL_ID="123456" uv run main.py
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
