"""Deterministic financial sentiment analyzer using domain lexicon and negation handling."""

import re

from src.contracts.news import SentimentScore
from src.finance_core.sentiment.base import BaseSentimentModel

# Loughran-McDonald inspired financial sentiment terms
FINANCIAL_POSITIVE = {
    "beat",
    "beats",
    "beating",
    "bullish",
    "growth",
    "profit",
    "profits",
    "profitable",
    "surge",
    "surged",
    "surging",
    "jump",
    "jumped",
    "gain",
    "gains",
    "gained",
    "outperform",
    "outperformed",
    "dividend",
    "dividends",
    "upgrade",
    "upgraded",
    "record",
    "highs",
    "momentum",
    "recovery",
    "expansion",
    "exceed",
    "exceeded",
    "exceeding",
    "strong",
    "rally",
    "rallied",
    "upside",
    "innovation",
    "innovative",
    "success",
    "successful",
    "breakthrough",
    "acquisition",
    "partnership",
    "all-time",
    "guidance",
    "raise",
    "raised",
}

FINANCIAL_NEGATIVE = {
    "miss",
    "misses",
    "missed",
    "bearish",
    "loss",
    "losses",
    "plunge",
    "plunged",
    "drop",
    "drops",
    "dropped",
    "fall",
    "fell",
    "slump",
    "slumped",
    "downgrade",
    "downgraded",
    "lawsuit",
    "sued",
    "fraud",
    "probe",
    "investigation",
    "subpoena",
    "breach",
    "layoff",
    "layoffs",
    "default",
    "bankruptcy",
    "debt",
    "inflation",
    "recession",
    "downside",
    "warning",
    "warns",
    "warned",
    "slashed",
    "cut",
    "weak",
    "decline",
    "declined",
    "declining",
    "underperform",
    "underperformed",
    "penalty",
}

NEGATION_TERMS = {
    "not",
    "no",
    "never",
    "without",
    "neither",
    "hardly",
    "scarcely",
    "cannot",
    "failed",
}


class FinancialLexiconSentimentModel(BaseSentimentModel):
    """Deterministic financial sentiment model with entity context and negation windows."""

    def __init__(self, model_name: str = "finance_sentiment_lexicon_v1"):
        self._name = model_name

    @property
    def model_name(self) -> str:
        return self._name

    def score(
        self,
        text: str,
        entity: str | None = None,
        max_chars: int = 12000,
    ) -> SentimentScore:
        clean_text = text[:max_chars].lower()
        tokens = re.findall(r"\b[a-z'-]+\b", clean_text)
        if not tokens:
            return SentimentScore(
                label="neutral",
                score=0.0,
                model=self.model_name,
                confidence=0.5,
                explanation="Empty or non-textual input",
            )

        pos_count = 0
        neg_count = 0
        window = 3

        for i, word in enumerate(tokens):
            has_negation = any(tokens[j] in NEGATION_TERMS for j in range(max(0, i - window), i))

            if word in FINANCIAL_POSITIVE:
                if has_negation:
                    neg_count += 1
                else:
                    pos_count += 1
            elif word in FINANCIAL_NEGATIVE:
                if has_negation:
                    pos_count += 1
                else:
                    neg_count += 1

        total_signals = pos_count + neg_count
        if total_signals == 0:
            return SentimentScore(
                label="neutral",
                score=0.0,
                model=self.model_name,
                confidence=0.6,
                explanation="No explicit financial sentiment indicators detected",
            )

        # Normalized scalar score in [-1.0, 1.0]
        net_score = (pos_count - neg_count) / total_signals
        confidence = min(1.0, 0.5 + (total_signals / 20.0))

        if net_score > 0.15:
            label = "positive"
        elif net_score < -0.15:
            label = "negative"
        else:
            label = "neutral"

        explanation = f"Detected {pos_count} positive and {neg_count} negative financial terms"
        return SentimentScore(
            label=label,
            score=round(net_score, 4),
            model=self.model_name,
            confidence=round(confidence, 4),
            explanation=explanation,
        )
