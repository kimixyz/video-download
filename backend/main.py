import os
import shutil
import subprocess
import tempfile
import urllib.parse
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask
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


def _validated_delogo_filter(x: int, y: int, width: int, height: int) -> str:
    """Build a bounded FFmpeg delogo filter for user-selected watermark boxes."""
    if min(x, y) < 0:
        raise api_error(400, "invalid_delogo_box", "水印区域坐标不能为负数")
    if width < 8 or height < 8:
        raise api_error(400, "invalid_delogo_box", "水印区域宽高至少为 8 像素")
    if width > 1600 or height > 900 or (width * height) > 900_000:
        raise api_error(400, "invalid_delogo_box", "水印区域过大，请缩小后重试")
    return f"delogo=x={x}:y={y}:w={width}:h={height}:show=0"


async def _download_source_video(decoded_url: str, headers: dict[str, str], target: Path) -> None:
    async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
        async with client.stream("GET", decoded_url, headers=headers) as resp:
            resp.raise_for_status()
            with target.open("wb") as handle:
                async for chunk in resp.aiter_bytes(chunk_size=65536):
                    handle.write(chunk)


def _run_ffmpeg_delogo(input_path: Path, output_path: Path, filter_expr: str) -> None:
    if shutil.which("ffmpeg") is None:
        raise api_error(500, "ffmpeg_unavailable", "服务器未安装 FFmpeg，无法进行后处理去水印")

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(input_path),
        "-vf",
        filter_expr,
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "23",
        "-c:a",
        "copy",
        "-movflags",
        "+faststart",
        str(output_path),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=900)
    except subprocess.TimeoutExpired as exc:
        raise api_error(504, "ffmpeg_timeout", "视频后处理超时，请缩小视频或水印区域后重试") from exc
    except subprocess.CalledProcessError as exc:
        details = exc.stderr.strip() if os.getenv("DEBUG_ERRORS") == "1" else None
        raise api_error(500, "ffmpeg_failed", "视频后处理失败", details) from exc


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
    details = str(exc) if os.getenv("DEBUG_ERRORS") == "1" else None
    payload = ErrorResponse(
        error=ErrorDetail(code="internal_error", message="服务器内部错误", details=details),
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
    postprocess: str | None = Query(None, description="Optional post-process mode, e.g. delogo"),
    wm_x: int = Query(20, ge=0, description="Watermark box x coordinate"),
    wm_y: int = Query(20, ge=0, description="Watermark box y coordinate"),
    wm_w: int = Query(600, ge=8, description="Watermark box width"),
    wm_h: int = Query(110, ge=8, description="Watermark box height"),
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

    if postprocess:
        if postprocess != "delogo":
            raise api_error(400, "unsupported_postprocess", "暂不支持该后处理模式")

        filter_expr = _validated_delogo_filter(wm_x, wm_y, wm_w, wm_h)
        tmpdir = tempfile.mkdtemp(prefix="video_delogo_")
        input_path = Path(tmpdir) / "input.mp4"
        output_path = Path(tmpdir) / "output.mp4"
        try:
            await _download_source_video(decoded_url, headers, input_path)
            await run_in_threadpool(_run_ffmpeg_delogo, input_path, output_path, filter_expr)
        except Exception:
            shutil.rmtree(tmpdir, ignore_errors=True)
            raise

        def file_iterator():
            with output_path.open("rb") as handle:
                while chunk := handle.read(65536):
                    yield chunk

        return StreamingResponse(
            file_iterator(),
            media_type="video/mp4",
            headers={
                "Content-Disposition": f'attachment; filename="{safe_filename}"',
                "Cache-Control": "no-cache",
            },
            background=BackgroundTask(shutil.rmtree, tmpdir, ignore_errors=True),
        )

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
