import os
import urllib.parse
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
from starlette.concurrency import run_in_threadpool

from models import ErrorDetail, ErrorResponse, ParseRequest, ParseResponse
from parser import parse_video
from video_rules import referer_for_url


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


def api_error(status_code: int, code: str, message: str, details: str | None = None) -> HTTPException:
    error_detail = ErrorDetail(code=code, message=message, details=details)
    return HTTPException(status_code=status_code, detail=error_detail.model_dump(exclude_none=True))


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    detail = exc.detail
    if isinstance(detail, dict):
        error = ErrorDetail(
            code=str(detail.get("code") or ("bad_request" if exc.status_code < 500 else "server_error")),
            message=str(detail.get("message") or "请求失败"),
            details=str(detail["details"]) if detail.get("details") is not None else None,
        )
    else:
        error = ErrorDetail(
            code="bad_request" if exc.status_code < 500 else "server_error",
            message=str(detail),
        )
    payload = ErrorResponse(error=error)
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump(exclude_none=True))


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):  # noqa: BLE001
    payload = ErrorResponse(
        error=ErrorDetail(code="internal_error", message="服务器内部错误", details=str(exc)),
    )
    return JSONResponse(status_code=500, content=payload.model_dump(exclude_none=True))


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
        raise api_error(400, "invalid_url", "URL 不能为空")
    try:
        result = await run_in_threadpool(parse_video, url)
    except ValueError as exc:
        raise api_error(400, "parse_failed", str(exc)) from exc
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
        raise api_error(400, "invalid_download_url", "无效的视频地址")

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
        "Referer": referer_for_url(decoded_url),
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

