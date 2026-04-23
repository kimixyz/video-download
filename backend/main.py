import os
import urllib.parse
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from models import ParseRequest, ParseResponse
from parser import parse_video


# ── app setup ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Video Parser API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        *([os.getenv("FRONTEND_URL", "").rstrip("/")] if os.getenv("FRONTEND_URL") else []),
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/healthz")
async def healthcheck() -> dict[str, str]:
    """Lightweight healthcheck for Railway and other reverse proxies."""
    return {"status": "ok"}


# ── routes ─────────────────────────────────────────────────────────────────────

@app.post("/api/parse", response_model=ParseResponse)
async def parse(req: ParseRequest) -> ParseResponse:
    """Parse a video URL and return available formats."""
    url = req.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL 不能为空")
    try:
        result = parse_video(url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"服务器内部错误：{exc}") from exc
    return result


@app.get("/api/download")
async def download(
    url: str = Query(..., description="Encoded video URL"),
    filename: str = Query("video.mp4", description="Download filename"),
):
    """Proxy-stream a video URL to the client, bypassing hotlink protection."""
    decoded_url = urllib.parse.unquote(url)

    # Basic sanity check – must be an http/https URL
    if not decoded_url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="无效的视频地址")

    # Sanitize filename to prevent header injection
    safe_filename = urllib.parse.quote(filename.replace('"', "").replace("\n", "").replace("\r", ""))

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/17.0 Mobile/15E148 Safari/604.1"
            if any(d in decoded_url for d in ("douyin", "snssdk", "iesdouyin", "douyinstatic", "tiktok"))
            else (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        ),
        "Referer": _referer_for(decoded_url),
        "Accept": "*/*",
    }

    async def stream_generator():
        async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
            async with client.stream("GET", decoded_url, headers=headers) as resp:
                resp.raise_for_status()
                async for chunk in resp.aiter_bytes(chunk_size=65536):
                    yield chunk

    return StreamingResponse(
        stream_generator(),
        media_type="video/mp4",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_filename}"',
            "Cache-Control": "no-cache",
        },
    )


# ── helpers ───────────────────────────────────────────────────────────────────

def _referer_for(url: str) -> str:
    """Return an appropriate Referer header value based on the URL domain."""
    referer_map = [
        ("douyin.com", "https://www.douyin.com/"),
        ("snssdk.com", "https://www.douyin.com/"),
        ("douyinstatic.com", "https://www.douyin.com/"),
        ("ixigua.com", "https://www.ixigua.com/"),
        ("bilibili.com", "https://www.bilibili.com/"),
        ("xiaohongshu.com", "https://www.xiaohongshu.com/"),
        ("xhslink.com", "https://www.xiaohongshu.com/"),
        ("kuaishou.com", "https://www.kuaishou.com/"),
        ("weibo.com", "https://weibo.com/"),
        ("youtube.com", "https://www.youtube.com/"),
        ("tiktok.com", "https://www.tiktok.com/"),
        ("twitter.com", "https://twitter.com/"),
        ("x.com", "https://x.com/"),
    ]
    for domain, referer in referer_map:
        if domain in url:
            return referer
    return url  # fallback: use the URL itself as referer
