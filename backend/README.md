---
title: Video Parser API
emoji: 🎬
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# Video Parser API

FastAPI backend for the video-download project, deployed as a Hugging Face Space
(Docker SDK). It parses video share links via `yt-dlp` and proxy-streams the file
to the browser to bypass hotlink protection.

## Endpoints

- `GET  /healthz` — health check
- `POST /api/parse` — `{ "url": "<share link or text>" }` → available formats
- `GET  /api/download?url=<encoded>&filename=<name>` — proxy-stream a video

## Environment variables (set as Space *Variables / Secrets*)

| Name | Required | Purpose |
|------|----------|---------|
| `FRONTEND_URL` | yes | Exact frontend origin allowed by CORS, e.g. `https://video.example.com` |
| `YTDLP_COOKIES_FILE` | no | Path to a Netscape cookie file for bilibili / youtube / tiktok / twitter |
| `VIDEO_RULES_PATH` | no | Override path to `video-rules.json` (defaults to the bundled `shared/` copy) |
| `DEBUG_ERRORS` | no | Set to `1` to surface raw error details |

The container listens on port **7860** (matching `app_port` above).
