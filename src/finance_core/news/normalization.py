"""News article normalization and point-in-time filtering."""

import hashlib
import re
from collections.abc import Sequence
from datetime import datetime
from urllib.parse import urlparse, urlunparse

from src.contracts.news import NewsArticle
from src.finance_core.market_data.normalization import normalize_datetime


def canonicalize_url(url: str) -> str:
    """Strip tracking parameters and fragments from news URLs."""
    if not url:
        return ""
    parsed = urlparse(url.strip())
    # Keep scheme, netloc, path; strip query parameters like utm_*, ref, etc.
    # Preserve path without trailing slashes
    clean_path = parsed.path.rstrip("/")
    clean_netloc = parsed.netloc.lower()
    clean_netloc = clean_netloc.removeprefix("www.")
    return urlunparse((parsed.scheme.lower(), clean_netloc, clean_path, "", "", ""))


def generate_article_id(canonical_url: str, title: str) -> str:
    """Generate deterministic SHA-256 identifier for an article."""
    normalized_title = re.sub(r"\W+", " ", title.lower()).strip()
    raw = f"{canonical_url}|{normalized_title}".encode()
    return hashlib.sha256(raw).hexdigest()[:24]


def normalize_title(title: str) -> str:
    """Normalize whitespace and punctuation for title matching."""
    return re.sub(r"\s+", " ", title.strip())


def filter_news_point_in_time(
    articles: Sequence[NewsArticle],
    as_of: datetime,
    stale_news_seconds: int = 7200,
) -> list[NewsArticle]:
    """
    Enforce point-in-time correctness on news:
    Exclude any article where available_at > as_of or published_at > as_of.
    Updates freshness and staleness flags.
    """
    as_of_utc = normalize_datetime(as_of)
    valid_articles: list[NewsArticle] = []

    for art in articles:
        pub_utc = normalize_datetime(art.published_at)
        avail_utc = normalize_datetime(art.available_at) if art.available_at else pub_utc

        # Rule: article only knowable if available_at <= as_of
        if avail_utc > as_of_utc or pub_utc > as_of_utc:
            continue

        freshness_secs = max(0.0, (as_of_utc - pub_utc).total_seconds())
        is_stale = freshness_secs > stale_news_seconds

        updated_art = art.model_copy(
            update={
                "published_at": pub_utc,
                "retrieved_at": normalize_datetime(art.retrieved_at),
                "available_at": avail_utc,
                "freshness_seconds": freshness_secs,
                "is_stale": is_stale,
            }
        )
        valid_articles.append(updated_art)

    # Sort newest first, but within the valid historical window
    valid_articles.sort(key=lambda x: x.published_at, reverse=True)
    return valid_articles
