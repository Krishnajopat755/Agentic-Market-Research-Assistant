"""Sentiment package."""

from src.finance_core.sentiment.aggregator import aggregate_sentiment
from src.finance_core.sentiment.base import BaseSentimentModel
from src.finance_core.sentiment.dictionary import FinancialLexiconSentimentModel

__all__ = [
    "BaseSentimentModel",
    "FinancialLexiconSentimentModel",
    "aggregate_sentiment",
]
