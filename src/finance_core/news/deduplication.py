"""News deduplication using URLs, provider IDs, title similarity, and publication window."""

import re
from collections.abc import Sequence
from difflib import SequenceMatcher
from uuid import uuid4

from src.contracts.news import NewsArticle
from src.finance_core.news.normalization import canonicalize_url


def calculate_title_similarity(title1: str, title2: str) -> float:
    """Compute normalized token overlap similarity between two titles."""
    words1 = set(re.findall(r"\w+", title1.lower()))
    words2 = set(re.findall(r"\w+", title2.lower()))
    if not words1 or not words2:
        return 0.0
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    jaccard = len(intersection) / len(union)
    seq = SequenceMatcher(None, title1.lower(), title2.lower()).ratio()
    return max(jaccard, seq)


def deduplicate_news(
    articles: Sequence[NewsArticle],
    similarity_threshold: float = 0.82,
    time_window_seconds: float = 3600.0,
) -> tuple[list[NewsArticle], list[NewsArticle]]:
    """
    Deduplicate a sequence of news articles.
    Returns (unique_canonical_articles, all_articles_with_dup_flags).
    Canonical articles are prioritized by earlier retrieval or richer description.
    """
    processed: list[NewsArticle] = []
    canonical_articles: list[NewsArticle] = []

    # Map signatures to canonical group ID
    url_to_group: dict[str, str] = {}
    provider_id_to_group: dict[str, str] = {}

    for article in articles:
        canonical_url = canonicalize_url(article.article_url)
        is_dup = False
        dup_reason: str | None = None
        group_id: str | None = None

        # Check 1: Provider Article ID
        if article.provider_article_id and article.provider_article_id in provider_id_to_group:
            is_dup = True
            group_id = provider_id_to_group[article.provider_article_id]
            dup_reason = f"Exact provider article ID match ({article.provider_article_id})"

        # Check 2: Canonical URL
        elif canonical_url and canonical_url in url_to_group:
            is_dup = True
            group_id = url_to_group[canonical_url]
            dup_reason = f"Exact canonical URL match ({canonical_url})"

        # Check 3: Near-duplicate title and time window with existing canonicals
        if not is_dup:
            for canon in canonical_articles:
                time_diff = abs((article.published_at - canon.published_at).total_seconds())
                if time_diff <= time_window_seconds:
                    sim = calculate_title_similarity(article.title, canon.title)
                    if sim >= similarity_threshold:
                        is_dup = True
                        group_id = canon.duplicate_group_id
                        dup_reason = f"High title similarity ({sim:.2f}) within {int(time_diff)}s of '{canon.title[:40]}...'"
                        break

        if is_dup:
            tagged = article.model_copy(
                update={
                    "is_duplicate": True,
                    "duplicate_group_id": group_id,
                    "duplicate_reason": dup_reason,
                }
            )
            processed.append(tagged)
        else:
            new_group_id = str(uuid4())[:8]
            tagged = article.model_copy(
                update={
                    "is_duplicate": False,
                    "duplicate_group_id": new_group_id,
                    "duplicate_reason": None,
                }
            )
            if canonical_url:
                url_to_group[canonical_url] = new_group_id
            if article.provider_article_id:
                provider_id_to_group[article.provider_article_id] = new_group_id
            processed.append(tagged)
            canonical_articles.append(tagged)

    return canonical_articles, processed
