from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from src.routers.deps import SessionDep
from src.database.models import Event, Place, Registration
from src.services.sync_service import SyncService
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


router = APIRouter(prefix="/api")


class PlaceResponse(BaseModel):
    id: str
    name: str
    city: str
    address: str
    seats_pattern: List[List[int]]

    class Config:
        from_attributes = True


class EventResponse(BaseModel):
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

    model_config = ConfigDict(from_attributes=True)


class EventsListResponse(BaseModel):
    count: int
    next: Optional[str]
    previous: Optional[str]
    results: List[EventResponse]


class SeatsResponse(BaseModel):
    event_id: str
    available_seats: List[List[int]]


class TicketCreateRequest(BaseModel):
    event_id: str
    row: int
    seat: int
    email: str


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
        "results": [EventResponse.from_orm(e) for e in events],
    }


@router.get("/events/{event_id}", response_model=EventResponse)
def get_event(event_id: str, db: SessionDep):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Not Found")
    return EventResponse.from_orm(event)


@router.get("/events/{event_id}/seats", response_model=SeatsResponse)
def get_seats(event_id: str, db: SessionDep):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Not Found")

    place = event.place
    if not place:
        raise HTTPException(status_code=500, detail="Place missing")

    base = place.seats_pattern

    available = [[0 if seat == 1 else 0 for seat in row] for row in base]

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

    if req.row < 1 or req.row > len(place.seats_pattern):
        raise HTTPException(status_code=400, detail="Invalid row")

    if req.seat < 1 or req.seat > len(place.seats_pattern[req.row - 1]):
        raise HTTPException(status_code=400, detail="Invalid seat")

    existing = db.query(Registration).filter_by(
        event_id=req.event_id,
        row=req.row,
        seat=req.seat
    ).first()

    if existing:
        raise HTTPException(status_code=409, detail="Seat already taken")

    ticket = Registration(
        event_id=req.event_id,
        row=req.row,
        seat=req.seat,
        email=req.email,
    )
    db.add(ticket)

    event.number_of_visitors += 1

    db.commit()
    db.refresh(ticket)

    return {"ticket_id": ticket.ticket_id}


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
