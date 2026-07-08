import enum
from typing import List, Optional

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IntPKMixin, TimestampMixin


class SchemeLevel(str, enum.Enum):
    CENTRAL = "central"
    STATE = "state"


class RuleOperator(str, enum.Enum):
    EQ = "eq"
    NEQ = "neq"
    LT = "lt"
    LTE = "lte"
    GT = "gt"
    GTE = "gte"
    IN = "in"


class Scheme(Base, IntPKMixin, TimestampMixin):
    __tablename__ = "schemes"

    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    level: Mapped[SchemeLevel] = mapped_column(Enum(SchemeLevel, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    authority: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    benefits_summary: Mapped[str] = mapped_column(Text, nullable=False)
    official_url: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    documents: Mapped[List["SchemeDocument"]] = relationship(back_populates="scheme", cascade="all, delete-orphan")
    rules: Mapped[List["SchemeRule"]] = relationship(back_populates="scheme", cascade="all, delete-orphan")


class SchemeDocument(Base, IntPKMixin):
    __tablename__ = "scheme_documents"

    scheme_id: Mapped[int] = mapped_column(ForeignKey("schemes.id"), nullable=False)
    document_name: Mapped[str] = mapped_column(String(200), nullable=False)
    mandatory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    scheme: Mapped["Scheme"] = relationship(back_populates="documents")


class SchemeRule(Base, IntPKMixin):
    """
    A single deterministic eligibility predicate: `field operator value`.
    ALL rules attached to a scheme must evaluate true for a profile to be
    eligible (AND semantics) — see app/domain/eligibility_rule_engine.py.

    `field` must be one of the attributes on PatientProfile
    (app/schemas/janmitra.py). `value` is stored as a string and cast to the
    correct type at evaluation time based on `field`'s declared type.
    """

    __tablename__ = "scheme_rules"

    scheme_id: Mapped[int] = mapped_column(ForeignKey("schemes.id"), nullable=False)
    field: Mapped[str] = mapped_column(String(100), nullable=False)
    operator: Mapped[RuleOperator] = mapped_column(Enum(RuleOperator, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    value: Mapped[str] = mapped_column(String(200), nullable=False)

    scheme: Mapped["Scheme"] = relationship(back_populates="rules")
