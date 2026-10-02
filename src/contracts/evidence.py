"""Evidence binding and lineage contracts."""

from datetime import datetime

from pydantic import BaseModel, Field


class ResearchEvidence(BaseModel):
    """Structured evidence backing a specific factual claim in the research report."""

    claim_id: str = Field(..., description="Unique claim identifier e.g. claim-123")
    claim_text: str = Field(..., description="The factual or analytical assertion made")
    evidence_type: str = Field(..., description="market, news, indicator, or model")
    evidence_ref: str = Field(..., description="Artifact URI or provider record ID")
    source_url: str | None = None
    source_timestamp: datetime | None = None
    calculation_ref: str | None = None


class ClaimValidationResult(BaseModel):
    """Validation report ensuring all material claims in report map to valid evidence."""

    is_valid: bool
    total_claims: int
    verified_claims: int
    unsupported_claims: list[str] = Field(default_factory=list)
