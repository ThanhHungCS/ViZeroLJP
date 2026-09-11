from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

VerdictLabel = Literal["A_WIN", "PARTIAL_A_WIN", "PARTIAL_B_WIN", "B_WIN"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CaseInput(StrictModel):
    case_id: str
    case_fact: str


class DispositionAssessment(StrictModel):
    source_quality: Literal[
        "OPERATIVE_ORDER", "COURT_REASONING", "PARTY_STATEMENT", "MISSING"
    ] = "MISSING"
    court_wording: Literal["ALL", "PARTIAL", "NONE", "NOT_EXPLICIT"] = (
        "NOT_EXPLICIT"
    )
    claim_scope: Literal["ALL", "MAJORITY", "MINORITY", "NONE", "UNCLEAR"] = (
        "UNCLEAR"
    )
    confidence: float = Field(default=0.5, ge=0, le=1)
    requested_relief: str = ""
    granted_relief: str = ""
    rejected_relief: str = ""
    decisive_chunk_ids: list[str] = Field(default_factory=list, max_length=6)
    followup_queries: list[str] = Field(default_factory=list, max_length=3)

    @field_validator("confidence", mode="before")
    @classmethod
    def normalize_confidence(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip().removesuffix("%").strip()
        try:
            number = float(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return value
        return number / 100 if 1 < number <= 100 else number


class LJPLabelPrediction(StrictModel):
    prediction: VerdictLabel
    confidence: float = Field(default=0.5, ge=0, le=1)
    explanation: str = ""

    @field_validator("confidence", mode="before")
    @classmethod
    def normalize_confidence(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip().removesuffix("%").strip()
        try:
            number = float(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return value
        return number / 100 if 1 < number <= 100 else number
