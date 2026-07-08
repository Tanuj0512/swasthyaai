from typing import List

from sqlalchemy import or_, select

from app.models.scheme import Scheme, SchemeRule
from app.repositories.base import BaseRepository


class SchemeRepository(BaseRepository[Scheme]):
    model = Scheme

    def list_active(self) -> List[Scheme]:
        stmt = select(Scheme).where(Scheme.is_active.is_(True))
        return list(self.db.execute(stmt).scalars().all())

    def search(self, keywords: List[str]) -> List[Scheme]:
        """Simple keyword retrieval over name/description/benefits — the
        deliberately low-tech 'R' in the Retrieval + Rules + AI architecture.
        No vector DB is needed at this catalogue size (a few dozen schemes);
        this is easier to audit and cheaper to run than an embeddings
        pipeline, and just as effective here."""
        if not keywords:
            return self.list_active()
        conditions = []
        for kw in keywords:
            like = f"%{kw}%"
            conditions.append(Scheme.name.ilike(like))
            conditions.append(Scheme.description.ilike(like))
            conditions.append(Scheme.benefits_summary.ilike(like))
        stmt = select(Scheme).where(Scheme.is_active.is_(True), or_(*conditions))
        return list(self.db.execute(stmt).scalars().all())


class SchemeRuleRepository(BaseRepository[SchemeRule]):
    model = SchemeRule

    def list_for_scheme(self, scheme_id: int) -> List[SchemeRule]:
        stmt = select(SchemeRule).where(SchemeRule.scheme_id == scheme_id)
        return list(self.db.execute(stmt).scalars().all())
