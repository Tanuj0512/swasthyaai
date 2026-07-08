from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import select

from app.models.inventory import Medicine, MedicineConsumptionLog, MedicineStock
from app.repositories.base import BaseRepository


class MedicineRepository(BaseRepository[Medicine]):
    model = Medicine

    def list_all(self) -> List[Medicine]:
        return list(self.db.execute(select(Medicine)).scalars().all())


class MedicineStockRepository(BaseRepository[MedicineStock]):
    model = MedicineStock

    def get_for_phc_and_medicine(self, phc_id: int, medicine_id: int) -> Optional[MedicineStock]:
        stmt = select(MedicineStock).where(
            MedicineStock.phc_id == phc_id, MedicineStock.medicine_id == medicine_id
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_for_phc(self, phc_id: int) -> List[MedicineStock]:
        stmt = select(MedicineStock).where(MedicineStock.phc_id == phc_id)
        return list(self.db.execute(stmt).scalars().all())

    def list_for_medicine_across_phcs(self, medicine_id: int) -> List[MedicineStock]:
        stmt = select(MedicineStock).where(MedicineStock.medicine_id == medicine_id)
        return list(self.db.execute(stmt).scalars().all())

    def list_below_threshold(self) -> List[MedicineStock]:
        stmt = select(MedicineStock, Medicine).join(Medicine, MedicineStock.medicine_id == Medicine.id)
        rows = self.db.execute(stmt).all()
        return [stock for stock, medicine in rows if stock.quantity <= medicine.reorder_threshold]


class MedicineConsumptionRepository(BaseRepository[MedicineConsumptionLog]):
    model = MedicineConsumptionLog

    def list_recent(self, phc_id: int, medicine_id: int, days: int) -> List[MedicineConsumptionLog]:
        since = datetime.utcnow() - timedelta(days=days)
        stmt = select(MedicineConsumptionLog).where(
            MedicineConsumptionLog.phc_id == phc_id,
            MedicineConsumptionLog.medicine_id == medicine_id,
            MedicineConsumptionLog.logged_at >= since,
        )
        return list(self.db.execute(stmt).scalars().all())
