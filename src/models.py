from __future__ import annotations

from typing import List
from pydantic import BaseModel, Field, ConfigDict


class ContractChangeOutput(BaseModel):
    """Validated output required by the LegalMove assignment."""

    model_config = ConfigDict(extra="forbid")

    sections_changed: List[str] = Field(
        ..., description="Identifiers or names of clauses/sections changed by the amendment."
    )
    topics_touched: List[str] = Field(
        ..., description="Legal or commercial topics affected by the detected changes."
    )
    summary_of_the_change: str = Field(
        ..., description="Precise, human-readable summary of all relevant changes."
    )
