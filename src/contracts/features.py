"""Research feature set contract."""

from datetime import datetime

from pydantic import BaseModel, Field


class ResearchFeatures(BaseModel):
    """Normalized research feature vector generated strictly point-in-time."""

    symbol: str
    as_of: datetime
    features: dict[str, float] = Field(
        ..., description="Key-value mapping of feature names to scalar floats"
    )
    feature_schema_version: str = "v1"
    feature_names: list[str] = Field(default_factory=list)
    artifact_ref: str | None = None
