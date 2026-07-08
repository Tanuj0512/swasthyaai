from app.models.ai_log import AIInteractionLog, EligibilityCheckLog
from app.repositories.base import BaseRepository


class AIInteractionLogRepository(BaseRepository[AIInteractionLog]):
    model = AIInteractionLog


class EligibilityCheckLogRepository(BaseRepository[EligibilityCheckLog]):
    model = EligibilityCheckLog
