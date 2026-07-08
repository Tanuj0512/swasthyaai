"""
Alembic's env.py imports `Base` from this module. Importing app.models here
(even though nothing in this file references the names directly) registers
every table on `Base.metadata`, which is what makes `alembic revision
--autogenerate` see the full schema.
"""

from app.models import Base  # noqa: F401
from app.models import (  # noqa: F401
    District,
    PHC,
    Medicine,
    MedicineStock,
    MedicineConsumptionLog,
    Bed,
    Doctor,
    DoctorAttendance,
    PatientFootfall,
    Alert,
    Scheme,
    SchemeDocument,
    SchemeRule,
    StaffProfile,
    AIInteractionLog,
    EligibilityCheckLog,
)
