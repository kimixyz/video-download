from __future__ import annotations

import json
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any


def _resolve_rules_path() -> Path:
    """Locate shared/video-rules.json across both monorepo and standalone deploys.

    Lookup order:
      1. $VIDEO_RULES_PATH (explicit override)
      2. ../shared/video-rules.json (monorepo layout — single source of truth in dev)
      3. ./shared/video-rules.json next to this module (bundled copy for standalone
         deploys such as a Hugging Face Space where ../shared is unavailable)
    """
    here = Path(__file__).resolve()
    candidates = [
        Path(os.environ["VIDEO_RULES_PATH"]) if os.getenv("VIDEO_RULES_PATH") else None,
        here.parents[1] / "shared" / "video-rules.json",
        here.parent / "shared" / "video-rules.json",
    ]
    for candidate in candidates:
        if candidate and candidate.is_file():
            return candidate
    raise FileNotFoundError(
        "video-rules.json not found. Set VIDEO_RULES_PATH or bundle it under backend/shared/."
    )


@lru_cache(maxsize=1)
def load_video_rules() -> dict[str, Any]:
    with _resolve_rules_path().open("r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def get_share_url_pattern() -> re.Pattern[str]:
    return re.compile(load_video_rules()["shareTextUrlPattern"])


def get_share_url_trailing_pattern() -> re.Pattern[str]:
    return re.compile(load_video_rules()["shareTextTrailingPunctuationPattern"])


def get_platforms() -> list[dict[str, Any]]:
    return list(load_video_rules()["platforms"])


def extract_share_url(text: str) -> str:
    match = get_share_url_pattern().search(text)
    if match:
        return get_share_url_trailing_pattern().sub("", match.group(0))
    return text.strip()


def detect_platform(url: str) -> str:
    for platform in get_platforms():
        if any(alias in url for alias in platform["aliases"]):
            return str(platform["id"])
    return "unknown"


def platform_label(platform_id: str) -> str:
    for platform in get_platforms():
        if platform["id"] == platform_id:
            return str(platform["displayName"])
    return platform_id


def referer_for_url(url: str) -> str:
    for platform in get_platforms():
        if any(alias in url for alias in platform["aliases"]):
            return str(platform["referer"])
    return url


def browser_cookie_platforms() -> set[str]:
    return {
        str(platform["id"])
        for platform in get_platforms()
        if platform.get("useBrowserCookies")
    }