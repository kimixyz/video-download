from pydantic import BaseModel
from typing import Optional


class ParseRequest(BaseModel):
    url: str


class VideoFormat(BaseModel):
    format_id: str
    quality: str
    ext: str
    url: str
    filesize: Optional[int] = None
    vcodec: Optional[str] = None
    acodec: Optional[str] = None


class ParseResponse(BaseModel):
    title: str
    thumbnail: Optional[str] = None
    author: Optional[str] = None
    platform: str
    duration: Optional[int] = None
    formats: list[VideoFormat]


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[str] = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
