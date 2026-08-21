"""Build a compliant Pinterest v5 Pin request body (minus board_id + media)."""

import re

TITLE_MAX = 100
DESC_MAX = 500
LINK_MAX = 2048


def build_pin_body(title, description, link):
    title = (title or "").strip()
    description = (description or "").strip()
    if not title:
        raise ValueError("title required")
    if len(title) > TITLE_MAX:
        title = title[: TITLE_MAX - 3].rstrip() + "..."
    if len(description) > DESC_MAX:
        description = description[: DESC_MAX - 3].rstrip() + "..."
    if not link:
        raise ValueError("link required")
    if len(link) > LINK_MAX:
        raise ValueError("link exceeds 2048 chars")
    return {
        "title": title,
        "description": description,
        "link": link,
    }
