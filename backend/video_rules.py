from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any


RULES_PATH = Path(__file__).resolve().parents[1] / "shared" / "video-rules.json"


@lru_cache(maxsize=1)
def load_video_rules() -> dict[str, Any]:
    with RULES_PATH.open("r", encoding="utf-8") as file_handle:
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