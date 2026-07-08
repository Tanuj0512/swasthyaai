from typing import Optional

from pydantic import BaseModel, ConfigDict


class CurrentStaff(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    phc_id: Optional[int] = None
    district_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
