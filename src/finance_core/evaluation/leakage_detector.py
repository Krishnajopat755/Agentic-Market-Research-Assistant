"""Point-in-time leakage detector and look-ahead bias verification suite."""

from collections.abc import Sequence
from datetime import datetime

from src.contracts.errors import ErrorCode, FinanceAppException
from src.contracts.market import MarketObservation
from src.contracts.news import NewsArticle
from src.finance_core.features.builder import build_research_features
from src.finance_core.indicators.technical import compute_technical_indicators
from src.finance_core.news.normalization import filter_news_point_in_time
from src.finance_core.sentiment.aggregator import aggregate_sentiment
from src.finance_core.signal.scorecard import compute_scorecard_signal


def verify_lookahead_bias(
    symbol: str,
    as_of: datetime,
    historical_market_bars: Sequence[MarketObservation],
    future_tampered_market_bars: Sequence[MarketObservation],
    historical_news: Sequence[NewsArticle],
    future_tampered_news: Sequence[NewsArticle],
) -> dict[str, bool]:
    """
    Mandatory Rule 2 / Section 10 verification:
    Compute indicators, sentiment, features, and signal using historical set.
    Compute indicators, sentiment, features, and signal using tampered future set.
    Assert they are completely identical as of cutoff T.
    """
    # 1. Base run
    tech_base = compute_technical_indicators(symbol, historical_market_bars, as_of=as_of)
    valid_news_base = filter_news_point_in_time(historical_news, as_of=as_of)
    sent_base = aggregate_sentiment(symbol, valid_news_base, as_of=as_of)
    feat_base = build_research_features(
        symbol, as_of=as_of, technical=tech_base, sentiment=sent_base
    )
    sig_base = compute_scorecard_signal(feat_base)

    # 2. Tampered run (contains modified or added data strictly after as_of)
    tech_tampered = compute_technical_indicators(symbol, future_tampered_market_bars, as_of=as_of)
    valid_news_tampered = filter_news_point_in_time(future_tampered_news, as_of=as_of)
    sent_tampered = aggregate_sentiment(symbol, valid_news_tampered, as_of=as_of)
    feat_tampered = build_research_features(
        symbol, as_of=as_of, technical=tech_tampered, sentiment=sent_tampered
    )
    sig_tampered = compute_scorecard_signal(feat_tampered)

    # 3. Assertions
    checks = {
        "technical_price_identical": tech_base.price == tech_tampered.price,
        "technical_sma_identical": tech_base.sma_20 == tech_tampered.sma_20,
        "technical_rsi_identical": tech_base.rsi_14 == tech_tampered.rsi_14,
        "news_count_identical": sent_base.article_count == sent_tampered.article_count,
        "news_mean_identical": sent_base.mean_score == sent_tampered.mean_score,
        "feature_vector_identical": feat_base.features == feat_tampered.features,
        "signal_score_identical": sig_base.score == sig_tampered.score,
        "signal_state_identical": sig_base.state == sig_tampered.state,
    }

    failed_checks = [name for name, passed in checks.items() if not passed]
    if failed_checks:
        raise FinanceAppException(
            error_code=ErrorCode.POINT_IN_TIME_VIOLATION,
            message=f"Point-in-time leakage detected in checks: {failed_checks}. Future data corrupted analysis at {as_of.isoformat()}",
            details={"failed_checks": failed_checks},
        )

    return checks
