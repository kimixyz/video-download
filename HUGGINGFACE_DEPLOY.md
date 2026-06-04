# Hugging Face Spaces Deployment (backend)

Replaces the expired Railway backend. The backend now runs as a **Docker Space**
on Hugging Face; the frontend stays on Vercel and points to the new Space URL.

## Why this works for free

- HF free CPU Spaces give 16 GB RAM and generous egress — fine for `yt-dlp`
  parsing **and** the `/api/download` proxy-stream.
- The Space sleeps after long inactivity and wakes on the next request
  (first request after sleep is slower). No hard request/bandwidth caps like
  serverless tiers.

## 1. Create the Space

1. Go to https://huggingface.co/new-space
2. Owner: your account · Space name: e.g. `video-parser-api`
3. **SDK: Docker** → "Blank"
4. Visibility: Public (free) is fine — no secrets live in the code.

This creates a git repo at `https://huggingface.co/spaces/<you>/video-parser-api`.

## 2. Push the backend to the Space

The Space repo must contain the **contents of `backend/`** at its root
(`Dockerfile` + `README.md` with HF metadata + the bundled `shared/`).

```bash
# from the monorepo root
git clone https://huggingface.co/spaces/<you>/video-parser-api hf-space
cp -R backend/. hf-space/
cd hf-space
# (optional) authenticate: huggingface-cli login  OR use a write token in the URL
git add -A
git commit -m "Deploy video parser backend"
git push
```

HF builds the Docker image automatically. Watch the **Logs** tab until it shows
`Uvicorn running on http://0.0.0.0:7860`. Your API base is:

```
https://<you>-video-parser-api.hf.space
```

Verify:

```bash
curl https://<you>-video-parser-api.hf.space/healthz   # -> {"status":"ok"}
```

## 3. Set Space variables

In the Space → **Settings → Variables and secrets**, add:

| Name | Value |
|------|-------|
| `FRONTEND_URL` | your exact frontend origin, e.g. `https://video.example.com` (no trailing slash) |

Optional:

- `YTDLP_COOKIES_FILE` — only if you also commit a Netscape `cookies.txt` and
  want bilibili / youtube / tiktok / twitter to use it (these need login cookies).
- `DEBUG_ERRORS=1` — to see raw error text while debugging.

After changing variables, restart the Space (Settings → Factory rebuild / Restart).

## 4. Point the frontend at the Space (Vercel)

In the Vercel project → **Settings → Environment Variables**:

```
NEXT_PUBLIC_API_BASE_URL = https://<you>-video-parser-api.hf.space
```

Then **redeploy** the frontend. The browser will now call the Space directly,
and the dev `/api/*` proxy in `frontend/next.config.ts` is bypassed in production.

> This is exactly why parsing currently errors on your custom domain: Railway is
> down, so `NEXT_PUBLIC_API_BASE_URL` points at a dead backend. Repointing it here fixes it.

## 5. CORS sanity check

`backend/main.py` allows `localhost:3000`, `127.0.0.1:3000`, and `FRONTEND_URL`.
Make sure `FRONTEND_URL` matches the origin in your browser's address bar
**exactly** (scheme + host, no path, no trailing slash), or the browser will
block the response.

## Keeping the rules file in sync

The single source of truth is `shared/video-rules.json`. `backend/shared/video-rules.json`
is a bundled copy so the Space is self-contained. After editing the shared rules,
re-sync before pushing to HF:

```bash
cp shared/video-rules.json backend/shared/video-rules.json
```

(In local dev the backend always reads the monorepo `shared/` copy, so no drift there.)

## Notes / limitations

- **No `cookiesfrombrowser`**: a headless Space has no Chrome. Platforms that need
  login (bilibili / youtube / tiktok / twitter) only work if you supply
  `YTDLP_COOKIES_FILE`. Douyin / Xigua / Toutiao / Weibo / Xiaohongshu / Kuaishou
  work without cookies.
- **Cold start**: first request after the Space sleeps takes longer — consider a
  cron ping to `/healthz` if you want it always warm.
- **No ffmpeg in the image**: the app streams a single direct format URL and never
  merges server-side, so ffmpeg isn't required.
```
