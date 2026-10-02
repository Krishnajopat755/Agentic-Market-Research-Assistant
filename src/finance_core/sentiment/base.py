"""Sentiment model abstract base interface."""

from abc import ABC, abstractmethod

from src.contracts.news import SentimentScore


class BaseSentimentModel(ABC):
    """Abstract interface for sentiment analyzers."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Identifier and version of the model."""

    @abstractmethod
    def score(
        self,
        text: str,
        entity: str | None = None,
        max_chars: int = 12000,
    ) -> SentimentScore:
        """Score article text and return standardized SentimentScore."""
