from typing import List, Optional

from sqlalchemy import select

from app.models.district import PHC, District
from app.repositories.base import BaseRepository


class DistrictRepository(BaseRepository[District]):
    model = District

    def get_by_name(self, name: str) -> Optional[District]:
        stmt = select(District).where(District.name == name)
        return self.db.execute(stmt).scalar_one_or_none()


class PHCRepository(BaseRepository[PHC]):
    model = PHC

    def list_by_district(self, district_id: int) -> List[PHC]:
        stmt = select(PHC).where(PHC.district_id == district_id)
        return list(self.db.execute(stmt).scalars().all())

    def list_all(self) -> List[PHC]:
        stmt = select(PHC)
        return list(self.db.execute(stmt).scalars().all())
