"""
Vercel serverless function: POST /api/parse
File-based routing: this file is served at /api/parse automatically.
"""
import sys
import os

# Ensure sibling modules (models, parser) are importable
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import ParseRequest, ParseResponse
from video_parser import parse_video

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
    allow_methods=["POST"],
    allow_headers=["*"],
)


@app.post("/api/parse", response_model=ParseResponse)
@app.post("/", response_model=ParseResponse)
async def parse(req: ParseRequest) -> ParseResponse:
    url = req.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL 不能为空")
    try:
        result = parse_video(url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"服务器内部错误：{exc}") from exc
    return result
