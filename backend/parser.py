import json
import re
from typing import Optional

import httpx
import yt_dlp

from models import ParseResponse, VideoFormat


# ── platform detection ────────────────────────────────────────────────────────

PLATFORM_PATTERNS: list[tuple[str, str]] = [
    (r"douyin\.com|douyinvideo\.com|iesdouyin\.com", "douyin"),
    (r"ixigua\.com", "xigua"),
    (r"toutiao\.com|toutiaoimg\.com", "toutiao"),
    (r"bilibili\.com|b23\.tv", "bilibili"),
    (r"xiaohongshu\.com|xhslink\.com", "xiaohongshu"),
    (r"kuaishou\.com|gifshow\.com", "kuaishou"),
    (r"weibo\.com|t\.cn", "weibo"),
    (r"youtube\.com|youtu\.be", "youtube"),
    (r"tiktok\.com", "tiktok"),
    (r"twitter\.com|x\.com|t\.co", "twitter"),
]


def extract_url(text: str) -> str:
    """Extract the first http/https URL from share text (e.g. Douyin/WeChat share strings)."""
    match = re.search(r'https?://[^\s\u3000\uff0c\u3002\uff01\uff1f\u3001]+', text)
    if match:
        url = match.group(0)
        # Strip trailing punctuation that may have been captured
        url = re.sub(r'[.,;:!?\)\]\u3002\uff01\uff1f]+$', '', url)
        return _normalize_url(url)
    return text.strip()


def _normalize_url(url: str) -> str:
    """Light normalization — heavy redirect-following is done per-platform."""
    return url


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from yt-dlp error messages."""
    return re.sub(r'\x1b\[[0-9;]*m', '', text)


def detect_platform(url: str) -> str:
    for pattern, name in PLATFORM_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            return name
    return "unknown"


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

    # Platforms where reading Chrome cookies improves results
    cookie_platforms = {"bilibili", "youtube", "twitter", "tiktok"}
    if platform in cookie_platforms:
        opts["cookiesfrombrowser"] = ("chrome",)

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
    play_addr = video.get("play_addr") or {}
    # url_list contains full playback URLs; uri is just an identifier key
    play_urls: list[str] = play_addr.get("url_list") or []
    wm_url: str = play_urls[0] if play_urls else ""

    if not wm_url:
        raise ValueError("未找到可下载的视频链接")

    # Build a no-watermark URL by replacing playwm→play endpoint.
    # The `ratio` parameter selects quality: 1080p / 720p / 360p.
    def _nowm(wm: str, ratio: str) -> str:
        """Strip watermark and set quality ratio on aweme play URL."""
        url = re.sub(r'/playwm/', '/play/', wm)
        url = re.sub(r'ratio=[^&]+', f'ratio={ratio}', url)
        if 'ratio=' not in url:
            sep = '&' if '?' in url else '?'
            url += f'{sep}ratio={ratio}'
        return url

    height: int = video.get("height") or 0
    width: int = video.get("width") or 0
    is_portrait = height >= width  # 竖屏视频

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
            url=_nowm(wm_url, ratio),
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
