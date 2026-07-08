from typing import Optional

from sqlalchemy import select

from app.models.staff import StaffProfile
from app.repositories.base import BaseRepository


class StaffRepository(BaseRepository[StaffProfile]):
    model = StaffProfile

    def get_by_email(self, email: str) -> Optional[StaffProfile]:
        stmt = select(StaffProfile).where(StaffProfile.email == email)
        return self.db.execute(stmt).scalar_one_or_none()
