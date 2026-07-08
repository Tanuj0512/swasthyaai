"""
Generic repository base. Every specific repository (PHCRepository,
MedicineRepository, ...) extends this for the common CRUD it needs, and adds
its own domain-specific queries on top. This is what keeps SQLAlchemy
`Session`/`select()` calls out of the service layer entirely — services only
ever talk to repositories, never to the ORM session directly.
"""

from typing import Generic, List, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    model: Type[ModelType]

    def __init__(self, db: Session):
        self.db = db

    def get(self, id_: int | str) -> Optional[ModelType]:
        return self.db.get(self.model, id_)

    def list(self, limit: int = 100, offset: int = 0) -> List[ModelType]:
        stmt = select(self.model).limit(limit).offset(offset)
        return list(self.db.execute(stmt).scalars().all())

    def add(self, instance: ModelType) -> ModelType:
        self.db.add(instance)
        self.db.flush()
        self.db.refresh(instance)
        return instance

    def delete(self, instance: ModelType) -> None:
        self.db.delete(instance)
        self.db.flush()

    def commit(self) -> None:
        self.db.commit()
