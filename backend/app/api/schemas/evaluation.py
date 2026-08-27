from typing import Literal

from pydantic import BaseModel, Field


class JudgeResult(BaseModel):
    bias_score: float = Field(ge=0.0, le=1.0)
    hallucination_score: float = Field(ge=0.0, le=1.0)
    privacy_score: float = Field(ge=0.0, le=1.0)

    overall_risk: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)

    reason: str

    recommendation: Literal[
        "ALLOW",
        "REVIEW",
        "BLOCK"
    ]