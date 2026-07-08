from typing import List

from sqlalchemy import select

from app.models.alert import Alert, AlertType
from app.repositories.base import BaseRepository


class AlertRepository(BaseRepository[Alert]):
    model = Alert

    def list_for_phc(self, phc_id: int, unresolved_only: bool = True, limit: int = 20) -> List[Alert]:
        stmt = select(Alert).where(Alert.phc_id == phc_id)
        if unresolved_only:
            stmt = stmt.where(Alert.resolved.is_(False))
        stmt = stmt.order_by(Alert.created_at.desc()).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def exists_open_alert(self, phc_id: int, alert_type: AlertType, message: str) -> bool:
        stmt = select(Alert).where(
            Alert.phc_id == phc_id,
            Alert.type == alert_type,
            Alert.message == message,
            Alert.resolved.is_(False),
        )
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def list_all_unresolved(self) -> List[Alert]:
        stmt = select(Alert).where(Alert.resolved.is_(False))
        return list(self.db.execute(stmt).scalars().all())
