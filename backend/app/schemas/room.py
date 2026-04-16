from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RoomCreate(BaseModel):
    name: str

class RoomOut(BaseModel):
    id: int
    slug: str
    name: str
    is_active: bool
    host_id: int
    created_at: datetime
    ended_at: Optional[datetime] = None

    class config:
        from_attributes = True
        