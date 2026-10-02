"""News processing package."""

from src.finance_core.news.deduplication import deduplicate_news
from src.finance_core.news.normalization import (
    canonicalize_url,
    filter_news_point_in_time,
    generate_article_id,
    normalize_title,
)

__all__ = [
    "canonicalize_url",
    "deduplicate_news",
    "filter_news_point_in_time",
    "generate_article_id",
    "normalize_title",
]
