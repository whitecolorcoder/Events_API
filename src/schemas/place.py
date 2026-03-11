from pydantic import BaseModel
from uuid import UUID

class PlaceResponse(BaseModel):
    id: UUID
    name: str
    city: str
    address: str
    seats_pattern: list[list[int]]

    class Config:
        orm_mode = True
