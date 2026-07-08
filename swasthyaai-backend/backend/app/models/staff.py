import enum
from typing import Optional

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class StaffRole(str, enum.Enum):
    PHC_STAFF = "phc_staff"
    DISTRICT_OFFICER = "district_officer"
    ADMIN = "admin"


class StaffProfile(Base, TimestampMixin):
    """
    Extends Supabase's `auth.users` table. `id` is the Supabase Auth user id
    (a UUID, issued by Supabase — never generated here). This is the only
    identity table our backend owns; authentication itself (password
    hashing, sessions, tokens) is entirely Supabase's responsibility, per the
    architecture decision to drop Firebase Auth and use one auth vendor.
    """

    __tablename__ = "staff_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    role: Mapped[StaffRole] = mapped_column(Enum(StaffRole, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    phc_id: Mapped[Optional[int]] = mapped_column(ForeignKey("phcs.id"), nullable=True)
    district_id: Mapped[Optional[int]] = mapped_column(ForeignKey("districts.id"), nullable=True)
