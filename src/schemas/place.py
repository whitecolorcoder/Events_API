from pydantic import BaseModel, ConfigDict
from uuid import UUID

class PlaceResponse(BaseModel):
    id: UUID
    name: str
    city: str
    address: str
    seats_pattern: list[list[int]]

    model_config = ConfigDict(from_attributes=True)
