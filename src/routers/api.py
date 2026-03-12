from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict

from src.database.models import Event, Registration
from src.routers.deps import SessionDep
from src.services.sync_service import SyncService

router = APIRouter(prefix="/api")


class PlaceResponse(BaseModel):
    id: str
    name: str
    city: str
    address: str
    seats_pattern: List[List[int]]

    class Config:
        from_attributes = True


class EventDetailResponse(BaseModel):
    id: str
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
        from_attributes = True


class EventListItem(BaseModel):
    id: str
    name: str
    place_id: str
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int
    created_at: datetime
    changed_at: datetime
    status_changed_at: datetime

    class Config:
        from_attributes = True


class EventsListResponse(BaseModel):
    count: int
    next: Optional[str]
    previous: Optional[str]
    results: List[EventListItem]


class SeatsResponse(BaseModel):
    event_id: str
    available_seats: List[List[int]]


class TicketCreateRequest(BaseModel):
    event_id: str
    first_name: str
    last_name: str
    email: str
    seat: str


class TicketCreateResponse(BaseModel):
    ticket_id: str


class TicketDeleteResponse(BaseModel):
    success: bool


@router.post("/sync/trigger")
def trigger_sync(db: SessionDep):
    SyncService(db).sync()
    return {"status": "ok"}


@router.get("/events", response_model=EventsListResponse)
def list_events(db: SessionDep):
    events = db.query(Event).all()
    return {
        "count": len(events),
        "next": None,
        "previous": None,
        "results": [EventListItem.from_orm(e) for e in events],
    }


@router.get("/events/{event_id}", response_model=EventDetailResponse)
def get_event(event_id: str, db: SessionDep):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Not Found")

    return EventDetailResponse(
        id=event.id,
        name=event.name,
        event_time=event.event_time,
        registration_deadline=event.registration_deadline,
        status=event.status,
        number_of_visitors=event.number_of_visitors,
        created_at=event.created_at,
        changed_at=event.changed_at,
        status_changed_at=event.status_changed_at,
        place=PlaceResponse.from_orm(event.place),
    )


@router.get("/events/{event_id}/seats", response_model=SeatsResponse)
def get_seats(event_id: str, db: SessionDep):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Not Found")

    place = event.place
    if not place:
        raise HTTPException(status_code=500, detail="Place missing")

    base = place.seats_pattern
    available = [[0 for _ in row] for row in base]

    registrations = db.query(Registration).filter_by(event_id=event_id).all()

    for r in registrations:
        available[r.row - 1][r.seat - 1] = 1

    return {
        "event_id": event_id,
        "available_seats": available,
    }


@router.post("/tickets", response_model=TicketCreateResponse, status_code=201)
def create_ticket(req: TicketCreateRequest, db: SessionDep):
    event = db.query(Event).filter(Event.id == req.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    place = event.place
    if not place:
        raise HTTPException(status_code=500, detail="Place missing")

    if len(req.seat) < 2:
        raise HTTPException(status_code=400, detail="Invalid seat format")

    row_letter = req.seat[0].upper()
    if not row_letter.isalpha():
        raise HTTPException(status_code=400, detail="Invalid seat row")

    try:
        seat_number = int(req.seat[1:])
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid seat number")

    row_index = ord(row_letter) - ord("A") + 1

    if row_index < 1 or row_index > len(place.seats_pattern):
        raise HTTPException(status_code=400, detail="Invalid row")

    if seat_number < 1 or seat_number > len(place.seats_pattern[row_index - 1]):
        raise HTTPException(status_code=400, detail="Invalid seat")

    existing = db.query(Registration).filter_by(
        event_id=req.event_id,
        row=row_index,
        seat=seat_number
    ).first()

    if existing:
        raise HTTPException(status_code=409, detail="Seat already taken")

    ticket = Registration(
        event_id=req.event_id,
        row=row_index,
        seat=seat_number,
        email=req.email,
        first_name=req.first_name,
        last_name=req.last_name,
    )

    db.add(ticket)
    event.number_of_visitors += 1
    db.commit()
    db.refresh(ticket)

    return TicketCreateResponse(ticket_id=ticket.ticket_id)


@router.delete("/tickets/{ticket_id}", response_model=TicketDeleteResponse)
def delete_ticket(ticket_id: str, db: SessionDep):
    ticket = db.query(Registration).filter(Registration.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    event = db.query(Event).filter(Event.id == ticket.event_id).first()
    if event:
        event.number_of_visitors -= 1

    db.delete(ticket)
    db.commit()

    return {"success": True}
