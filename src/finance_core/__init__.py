"""Deterministic finance core package."""

from src.finance_core.evaluation.leakage_detector import verify_lookahead_bias
from src.finance_core.evaluation.walk_forward import run_walk_forward_evaluation
from src.finance_core.features.builder import build_research_features
from src.finance_core.indicators.technical import compute_technical_indicators
from src.finance_core.market_data.normalization import (
    build_market_snapshot,
    filter_market_observations_point_in_time,
)
from src.finance_core.news.deduplication import deduplicate_news
from src.finance_core.news.normalization import filter_news_point_in_time
from src.finance_core.sentiment.aggregator import aggregate_sentiment
from src.finance_core.sentiment.dictionary import FinancialLexiconSentimentModel
from src.finance_core.signal.classifier import MLSignalClassifier
from src.finance_core.signal.scorecard import compute_scorecard_signal

__all__ = [
    "FinancialLexiconSentimentModel",
    "MLSignalClassifier",
    "aggregate_sentiment",
    "build_market_snapshot",
    "build_research_features",
    "compute_scorecard_signal",
    "compute_technical_indicators",
    "deduplicate_news",
    "filter_market_observations_point_in_time",
    "filter_news_point_in_time",
    "run_walk_forward_evaluation",
    "verify_lookahead_bias",
]
