"""Signal result and model evaluation contracts."""

from datetime import datetime

from pydantic import BaseModel, Field


class SignalContributor(BaseModel):
    """Component contribution to the overall signal score."""

    name: str
    weight: float
    value: float
    contribution: float
    direction: str = "BULLISH|BEARISH|NEUTRAL"


class SignalResult(BaseModel):
    """Final quantitative market research signal candidate."""

    symbol: str
    as_of: datetime
    horizon_bars: int = Field(default=5, description="Prediction horizon in bars")
    method: str = Field(..., description="scorecard, ml, or ensemble")
    model_version: str = Field(default="signal-model-1.0.0")
    state: str = Field(..., description="BULLISH, NEUTRAL, or BEARISH")
    score: float = Field(..., ge=-1.0, le=1.0, description="Normalized score in [-1.0, 1.0]")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Calibrated or heuristic confidence in [0.0, 1.0]"
    )
    feature_artifact_ref: str | None = None
    top_contributors: list[SignalContributor] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class WalkForwardEvaluationResult(BaseModel):
    """Walk-forward point-in-time time-series model evaluation metrics."""

    model_name: str
    model_version: str
    feature_schema_version: str
    train_splits_count: int
    total_test_samples: int
    accuracy: float
    balanced_accuracy: float
    macro_f1: float
    precision_by_class: dict[str, float]
    recall_by_class: dict[str, float]
    brier_score: float | None = None
    roc_auc: float | None = None
    evaluation_window: dict[str, str]
    lookahead_bias_passed: bool
