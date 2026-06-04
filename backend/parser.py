import json
import os
import re
import urllib.parse
from typing import Optional

import httpx
import yt_dlp

from models import ParseResponse, VideoFormat
from video_rules import (
    browser_cookie_platforms,
    detect_platform as shared_detect_platform,
    extract_share_url,
)


def extract_url(text: str) -> str:
    """Extract the first http/https URL from share text (e.g. Douyin/WeChat share strings)."""
    return _normalize_url(extract_share_url(text))


def _normalize_url(url: str) -> str:
    """Light normalization — heavy redirect-following is done per-platform."""
    return url


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from yt-dlp error messages."""
    return re.sub(r'\x1b\[[0-9;]*m', '', text)


def detect_platform(url: str) -> str:
    return shared_detect_platform(url)


# ── quality label ─────────────────────────────────────────────────────────────

def quality_label(fmt: dict) -> str:
    """Return a human-readable quality label, e.g. '1080P', '720P HD'."""
    height: Optional[int] = fmt.get("height")
    if height:
        label = f"{height}P"
        if height >= 1080:
            label += " HD"
        return label
    # Try bitrate as fallback
    tbr = fmt.get("tbr")
    if tbr:
        return f"{int(tbr)}kbps"
    # fallback to format_note or a friendly label
    note = fmt.get("format_note")
    if note and note not in ("none", "unknown"):
        return str(note)
    return "最佳画质"


# ── base ydl opts ─────────────────────────────────────────────────────────────

def _base_opts(platform: str) -> dict:
    """Return yt-dlp options tailored for the given platform."""
    opts: dict = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
        "skip_download": True,
        # Prefer mp4 with audio merged, fallback to best
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
    }

    # Platforms where cookies improve results (bilibili / youtube / tiktok / twitter).
    # On a headless server there is no local Chrome to read, so we accept an optional
    # Netscape-format cookie file via $YTDLP_COOKIES_FILE instead of cookiesfrombrowser.
    if platform in browser_cookie_platforms():
        cookie_file = os.getenv("YTDLP_COOKIES_FILE")
        if cookie_file and os.path.isfile(cookie_file):
            opts["cookiefile"] = cookie_file

    # Douyin: use Referer to get watermark-free stream
    if platform == "douyin":
        opts["http_headers"] = {
            "Referer": "https://www.douyin.com",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                "Version/17.0 Mobile/15E148 Safari/604.1"
            ),
        }

    # Bilibili: a desktop UA + Referer are required, otherwise the API rejects
    # the request with HTTP 412 (Precondition Failed) via its risk control.
    if platform == "bilibili":
        opts["http_headers"] = {
            "Referer": "https://www.bilibili.com/",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
        }

    return opts


# ── format filtering ──────────────────────────────────────────────────────────

def _is_downloadable(fmt: dict) -> bool:
    """Keep only formats that have a direct URL and carry video."""
    if not fmt.get("url"):
        return False
    vcodec = fmt.get("vcodec") or "none"
    acodec = fmt.get("acodec") or "none"
    # Exclude pure audio-only: vcodec is none but acodec is a real codec
    if vcodec == "none" and acodec not in ("none", "unknown"):
        return False
    # Exclude manifest/storyboard formats
    protocol = fmt.get("protocol", "")
    if protocol in ("mhtml",):
        return False
    return True


def _deduplicate_formats(formats: list[VideoFormat]) -> list[VideoFormat]:
    """Remove duplicate quality labels, keeping the highest filesize."""
    seen: dict[str, VideoFormat] = {}
    for f in formats:
        existing = seen.get(f.quality)
        if existing is None:
            seen[f.quality] = f
        else:
            # prefer the one with known filesize
            if f.filesize and (not existing.filesize or f.filesize > existing.filesize):
                seen[f.quality] = f
    return list(seen.values())


def _dedupe_strings(values: list[str]) -> list[str]:
    """Keep first occurrence order while removing duplicates and blanks."""
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = value.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def _extract_url_candidates(value: object) -> list[str]:
    """Collect URL-like strings from nested Douyin payloads."""
    urls: list[str] = []
    if isinstance(value, str):
        if value.startswith(("http://", "https://")):
            urls.append(value)
        return urls

    if isinstance(value, list):
        for item in value:
            urls.extend(_extract_url_candidates(item))
        return urls

    if isinstance(value, dict):
        for key in ("url_list", "backup_url_list", "play_addr", "download_addr", "bit_rate", "main_url", "src", "url"):
            if key in value:
                urls.extend(_extract_url_candidates(value[key]))
        return urls

    return urls


def _normalize_douyin_play_url(url: str, ratio: str | None = None) -> str:
    """Remove watermark hints and normalize a Douyin play URL.

    Douyin payloads are not fully stable. Some responses expose watermark URLs
    under `playwm`, while others expose `play` URLs with extra query params that
    still point at a watermarked rendition. This helper rewrites both shapes.
    """
    parsed = urllib.parse.urlsplit(url)
    path = parsed.path.replace("/playwm/", "/play/")
    path = path.replace("/playwm", "/play")

    query_items = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    cleaned_items: list[tuple[str, str]] = []
    for key, value in query_items:
        if key in {"watermark", "logo", "cut_type", "line", "value"}:
            continue
        cleaned_items.append((key, value))

    if ratio is not None:
        cleaned_items = [(key, value) for key, value in cleaned_items if key != "ratio"]
        cleaned_items.append(("ratio", ratio))

    rebuilt = parsed._replace(
        path=path,
        query=urllib.parse.urlencode(cleaned_items, doseq=True),
    )
    return urllib.parse.urlunsplit(rebuilt)


def _select_douyin_play_url(video: dict) -> str:
    """Pick the best available Douyin playback URL."""
    candidates = _dedupe_strings(
        _extract_url_candidates(video.get("play_addr"))
        + _extract_url_candidates(video.get("download_addr"))
        + _extract_url_candidates(video.get("bit_rate"))
    )
    if not candidates:
        raise ValueError("未找到可下载的视频链接")

    # Prefer already-clean play URLs before falling back to rewrite.
    for candidate in candidates:
        if "/play/" in candidate and "/playwm/" not in candidate:
            return candidate

    return candidates[0]


# ── douyin custom handler ─────────────────────────────────────────────────────

_DOUYIN_MOBILE_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/17.0 Mobile/15E148 Safari/604.1"
)


def _handle_douyin_url(url: str) -> tuple[Optional[ParseResponse], str]:
    """
    Follow Douyin short/share URL once and parse from HTML directly.
    This avoids yt-dlp's DouyinIE which requires fresh cookies.

    Returns:
        (ParseResponse, "")   — successfully parsed from HTML
        (None, original_url)  — network error, fallback to yt-dlp
    Raises:
        ValueError — for image notes (图文笔记) or unrecoverable errors
    """
    headers = {
        "User-Agent": _DOUYIN_MOBILE_UA,
        "Referer": "https://www.douyin.com",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    try:
        with httpx.Client(follow_redirects=True, timeout=15, headers=headers) as client:
            resp = client.get(url)
            final_url = str(resp.url)
            html = resp.text
    except Exception:
        return None, url  # Network error → fallback to yt-dlp with original URL

    # Both /share/video/ and /share/note/ pages carry _ROUTER_DATA we can parse
    if 'iesdouyin.com/share/' in final_url:
        return _parse_douyin_from_html(html), ""

    # Fallback: pass whatever URL we landed on to yt-dlp
    return None, final_url


def _parse_douyin_from_html(html: str) -> ParseResponse:
    """Parse video data from any Douyin iesdouyin share page (_ROUTER_DATA script block)."""
    scripts = re.findall(
        r'window\._ROUTER_DATA\s*=\s*(.*?)(?=\s*window\.|</script>)', html, re.DOTALL
    )
    if not scripts:
        raise ValueError("无法解析抖音笔记数据，请稍后重试")

    try:
        data = json.loads(scripts[0].strip().rstrip(";"))
    except json.JSONDecodeError as exc:
        raise ValueError("抖音笔记数据格式异常") from exc

    loader = data.get("loaderData") or {}
    page_data: Optional[dict] = None
    for val in loader.values():
        if isinstance(val, dict) and (val.get("videoInfoRes") or {}).get("item_list"):
            page_data = val
            break

    if not page_data:
        raise ValueError("无法找到抖音视频数据，请稍后重试")

    item_list = (page_data.get("videoInfoRes") or {}).get("item_list") or []
    if not item_list:
        raise ValueError("抖音视频内容为空")

    item = item_list[0]

    # Image carousel note (图文笔记) — no downloadable video
    if item.get("images"):
        raise ValueError("该内容为抖音图文笔记（多图+音乐），暂不支持视频下载")

    video = item.get("video") or {}
    source_url = _select_douyin_play_url(video)

    # 3 quality tiers (no watermark)
    quality_tiers = [
        ("high",   "1080p", "高清 1080P"),
        ("medium", "720p",  "标清 720P"),
        ("low",    "360p",  "流畅 360P"),
    ]

    formats: list[VideoFormat] = [
        VideoFormat(
            format_id=fid,
            quality=label,
            url=_normalize_douyin_play_url(source_url, ratio=ratio),
            ext="mp4",
            vcodec="h264",
            acodec="aac",
        )
        for fid, ratio, label in quality_tiers
    ]

    author_data = item.get("author") or {}
    cover = video.get("cover") or {}
    thumbnail = ((cover.get("url_list") or [None])[0]) or None
    raw_duration: int = video.get("duration") or 0
    duration = raw_duration // 1000 if raw_duration > 1000 else raw_duration

    return ParseResponse(
        title=item.get("desc") or "抖音视频",
        thumbnail=thumbnail,
        author=author_data.get("nickname"),
        platform="douyin",
        duration=duration or None,
        formats=formats,
    )


# ── bilibili url normalization ────────────────────────────────────────────────

_BILIBILI_DESKTOP_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


def _normalize_bilibili_url(url: str) -> str:
    """Resolve b23.tv short links and rewrite to the canonical desktop URL.

    yt-dlp's BiliBili extractor only matches ``www.bilibili.com/video/<id>``.
    Short links (b23.tv) and the mobile host (m.bilibili.com) fall through to
    the generic extractor, which Bilibili blocks with HTTP 412. We follow the
    redirect, extract the BV/av id, and rebuild a www URL yt-dlp recognizes.
    """
    resolved = url
    if "b23.tv" in url:
        try:
            with httpx.Client(
                follow_redirects=True, timeout=10,
                headers={"User-Agent": _BILIBILI_DESKTOP_UA},
            ) as client:
                resolved = str(client.get(url).url)
        except Exception:
            return url  # network failure → let yt-dlp try the original

    match = re.search(r"(BV[0-9A-Za-z]+|av\d+)", resolved)
    if not match:
        return resolved
    return f"https://www.bilibili.com/video/{match.group(1)}"


# ── main entry ────────────────────────────────────────────────────────────────

def parse_video(url: str) -> ParseResponse:
    """Extract video info from URL and return structured response."""
    # Handle share text that contains a URL mixed with description (e.g. Douyin share)
    url = extract_url(url)
    platform = detect_platform(url)

    # Douyin: follow redirect and parse HTML directly (yt-dlp DouyinIE requires cookies)
    if platform == "douyin":
        try:
            parsed, resolved_url = _handle_douyin_url(url)
            if parsed is not None:
                return parsed
            url = resolved_url
        except ValueError:
            raise
        except Exception:
            pass

    # Bilibili: expand b23.tv short links and rewrite to www host so yt-dlp's
    # BiliBili extractor matches (otherwise it falls to generic → HTTP 412).
    if platform == "bilibili":
        url = _normalize_bilibili_url(url)

    # Toutiao: follow redirect to resolve short URLs (e.g. m.toutiao.com/is/xxx/)
    if platform == "toutiao":
        try:
            with httpx.Client(follow_redirects=True, timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                              "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                              "Version/17.0 Mobile/15E148 Safari/604.1",
            }) as client:
                url = str(client.get(url).url)
        except Exception:
            pass

    # Xiaohongshu image-only detection will happen after extraction
    ydl_opts = _base_opts(platform)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except yt_dlp.utils.DownloadError as exc:
        raise ValueError(f"解析失败：{_strip_ansi(str(exc))}") from exc
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"解析出错：{_strip_ansi(str(exc))}") from exc

    if info is None:
        raise ValueError("无法获取视频信息，请检查链接是否有效")

    # Handle playlists (take first entry)
    if info.get("_type") == "playlist":
        entries = info.get("entries") or []
        if not entries:
            raise ValueError("播放列表为空")
        info = entries[0]
        if info is None:
            raise ValueError("无法获取视频信息")

    # Xiaohongshu: detect image-only posts
    if platform == "xiaohongshu":
        raw_formats = info.get("formats") or []
        has_video = any(
            (f.get("vcodec") or "none") != "none" for f in raw_formats
        )
        if not has_video and not info.get("url"):
            raise ValueError("该内容为图文，暂不支持下载")

    # Build format list
    raw_formats: list[dict] = info.get("formats") or []

    # If no separate formats list, wrap the single stream
    if not raw_formats and info.get("url"):
        raw_formats = [
            {
                "format_id": "best",
                "url": info["url"],
                "ext": info.get("ext") or "mp4",
                "vcodec": info.get("vcodec") or "none",
                "acodec": info.get("acodec"),
                "height": info.get("height"),
                "filesize": info.get("filesize"),
                "format_note": info.get("format_note"),
                "tbr": info.get("tbr"),
            }
        ]

    video_formats: list[VideoFormat] = []
    for fmt in raw_formats:
        if not _is_downloadable(fmt):
            continue
        video_formats.append(
                VideoFormat(
                    format_id=str(fmt.get("format_id", "best")),
                    quality=quality_label(fmt),
                    ext="mp4" if (fmt.get("ext") or "").startswith("unknown") else (fmt.get("ext") or "mp4"),
                    url=fmt["url"],
                    filesize=fmt.get("filesize") or fmt.get("filesize_approx"),
                    vcodec=fmt.get("vcodec"),
                    acodec=fmt.get("acodec"),
                )
            )

    if not video_formats:
        raise ValueError("未找到可下载的视频格式，链接可能受权限保护")

    # Sort by height descending (best quality first)
    def sort_key(f: VideoFormat) -> int:
        m = re.match(r"(\d+)P", f.quality)
        return int(m.group(1)) if m else 0

    video_formats.sort(key=sort_key, reverse=True)
    video_formats = _deduplicate_formats(video_formats)

    return ParseResponse(
        title=info.get("title") or "未知标题",
        thumbnail=info.get("thumbnail"),
        author=info.get("uploader") or info.get("creator") or info.get("channel"),
        platform=platform,
        duration=int(info["duration"]) if info.get("duration") is not None else None,
        formats=video_formats,
    )
