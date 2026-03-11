from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from src.schemas.place import PlaceResponse

class EventResponse(BaseModel):
    id: UUID
    name: str
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int
    created_at: datetime
    changed_at: datetime
    status_changed_at: datetime
    place: PlaceResponse

    class Config:
        orm_mode = True
