from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IntPKMixin, utcnow


class AIInteractionLog(Base, IntPKMixin):
    """
    Audit trail for every AI call made by the platform. Deliberately stores
    a hash of the input and a short output summary — never the raw prompt or
    any patient-identifying text — so this table is safe to inspect/export
    without becoming a second copy of sensitive data (see architecture
    decision #4: no patient PII persisted).
    """

    __tablename__ = "ai_interaction_log"

    module: Mapped[str] = mapped_column(String(50), nullable=False)  # inventory | janmitra | district | voice
    provider_used: Mapped[str] = mapped_column(String(30), nullable=False)
    prompt_template_version: Mapped[str] = mapped_column(String(20), nullable=False)
    input_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    output_summary: Mapped[str] = mapped_column(Text, nullable=False)
    guardrail_flags: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    succeeded: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class EligibilityCheckLog(Base, IntPKMixin):
    """Anonymized outcome only — no patient profile fields are stored."""

    __tablename__ = "eligibility_check_log"

    phc_id: Mapped[Optional[int]] = mapped_column(ForeignKey("phcs.id"), nullable=True)
    scheme_id: Mapped[int] = mapped_column(ForeignKey("schemes.id"), nullable=False)
    is_eligible: Mapped[bool] = mapped_column(Boolean, nullable=False)
    checked_by_role: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
