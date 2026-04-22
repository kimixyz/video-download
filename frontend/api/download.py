"""
Vercel serverless function: GET /api/download
File-based routing: this file is served at /api/download automatically.
"""
import sys
import os
import urllib.parse

# Ensure sibling modules are importable
sys.path.insert(0, os.path.dirname(__file__))

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

app = FastAPI()

_allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
_prod_origin = os.getenv("FRONTEND_URL", "")
if _prod_origin:
    _allowed_origins.append(_prod_origin.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)


def _referer_for(url: str) -> str:
    referer_map = [
        ("douyin.com",       "https://www.douyin.com/"),
        ("snssdk.com",       "https://www.douyin.com/"),
        ("douyinstatic.com", "https://www.douyin.com/"),
        ("zjcdn.com",        "https://www.douyin.com/"),
        ("ixigua.com",       "https://www.ixigua.com/"),
        ("bilibili.com",     "https://www.bilibili.com/"),
        ("xiaohongshu.com",  "https://www.xiaohongshu.com/"),
        ("xhslink.com",      "https://www.xiaohongshu.com/"),
        ("kuaishou.com",     "https://www.kuaishou.com/"),
        ("weibo.com",        "https://weibo.com/"),
        ("youtube.com",      "https://www.youtube.com/"),
        ("tiktok.com",       "https://www.tiktok.com/"),
        ("twitter.com",      "https://twitter.com/"),
        ("x.com",            "https://x.com/"),
    ]
    for domain, referer in referer_map:
        if domain in url:
            return referer
    return url


@app.get("/api/download")
@app.get("/")
async def download(
    url: str = Query(...),
    filename: str = Query("video.mp4"),
):
    decoded_url = urllib.parse.unquote(url)
    if not decoded_url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="无效的视频地址")

    _douyin_domains = ("douyin", "snssdk", "iesdouyin", "douyinstatic", "tiktok", "zjcdn")
    ua = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
        if any(d in decoded_url for d in _douyin_domains)
        else (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
    )

    req_headers = {
        "User-Agent": ua,
        "Referer": _referer_for(decoded_url),
    }

    safe_filename = urllib.parse.quote(
        filename.replace('"', "").replace("\n", "").replace("\r", "")
    )

    # Proxy the video content through our server so CDN anti-hotlink checks pass.
    # The server fetches with the correct Referer/UA and streams bytes to the client.
    async def stream_content():
        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            async with client.stream("GET", decoded_url, headers=req_headers) as resp:
                async for chunk in resp.aiter_bytes(65536):
                    yield chunk

    return StreamingResponse(
        stream_content(),
        media_type="video/mp4",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_filename}"',
            "Cache-Control": "no-cache",
        },
    )


_allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
_prod_origin = os.getenv("FRONTEND_URL", "")
if _prod_origin:
    _allowed_origins.append(_prod_origin.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)


def _referer_for(url: str) -> str:
    referer_map = [
        ("douyin.com",       "https://www.douyin.com/"),
        ("snssdk.com",       "https://www.douyin.com/"),
        ("douyinstatic.com", "https://www.douyin.com/"),
        ("ixigua.com",       "https://www.ixigua.com/"),
        ("bilibili.com",     "https://www.bilibili.com/"),
        ("xiaohongshu.com",  "https://www.xiaohongshu.com/"),
        ("xhslink.com",      "https://www.xiaohongshu.com/"),
        ("kuaishou.com",     "https://www.kuaishou.com/"),
        ("weibo.com",        "https://weibo.com/"),
        ("youtube.com",      "https://www.youtube.com/"),
        ("tiktok.com",       "https://www.tiktok.com/"),
        ("twitter.com",      "https://twitter.com/"),
        ("x.com",            "https://x.com/"),
    ]
    for domain, referer in referer_map:
        if domain in url:
            return referer
    return url


@app.get("/api/download")
@app.get("/")
async def download(
    url: str = Query(...),
    filename: str = Query("video.mp4"),
):
    decoded_url = urllib.parse.unquote(url)
    if not decoded_url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="无效的视频地址")

    _douyin_domains = ("douyin", "snssdk", "iesdouyin", "douyinstatic", "tiktok")
    ua = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
        if any(d in decoded_url for d in _douyin_domains)
        else (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
    )

    try:
        with httpx.Client(follow_redirects=True, timeout=10) as client:
            resp = client.head(
                decoded_url,
                headers={"User-Agent": ua, "Referer": _referer_for(decoded_url)},
            )
            final_url = str(resp.url)
    except Exception:
        final_url = decoded_url

    safe_filename = urllib.parse.quote(
        filename.replace('"', "").replace("\n", "").replace("\r", "")
    )

    return RedirectResponse(
        url=final_url,
        status_code=302,
        headers={"Content-Disposition": f'attachment; filename="{safe_filename}"'},
    )
