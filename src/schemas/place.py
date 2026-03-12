from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PlaceResponse(BaseModel):
    id: UUID
    name: str
    city: str
    address: str
    seats_pattern: list[list[int]]

    model_config = ConfigDict(from_attributes=True)
