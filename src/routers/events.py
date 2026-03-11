from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from src.routers.deps import SessionDep
from src.database.models import Event, Place, Registration
from src.services.events_provider_client import EventsProviderClient
from sqlalchemy.orm import joinedload
from src.schemas.event import EventResponse
from fastapi import Query


router = APIRouter(prefix="/events")

@router.get("", response_model=dict)
def list_events(
    db: SessionDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    total = db.query(Event).count()
    pages = (total + page_size - 1) // page_size

    events = (
        db.query(Event)
        .options(joinedload(Event.place))
        .order_by(Event.event_time)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": [EventResponse.from_orm(e) for e in events],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }

@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: str, db: SessionDep):
    event = (
        db.query(Event)
        .options(joinedload(Event.place))
        .filter(Event.id == event_id)
        .first()
    )

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return EventResponse.from_orm(event)

@router.get("/{event_id}/seats")
def get_seats(event_id: str, db: SessionDep):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if event.status != "published":
        raise HTTPException(status_code=400, detail="Event is not published")

    place = db.query(Place).filter(Place.id == event.place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")


    seats = []
    blocks = place.seats_pattern.split(",")  
    for block in blocks:
        row = block[0]         
        rng = block[1:]        
        start, end = map(int, rng.split("-"))
        for num in range(start, end + 1):
            seats.append(f"{row}{num}")

    taken = db.query(Registration.seat).filter(
        Registration.event_id == event_id
    ).all()
    taken_seats = {t[0] for t in taken}

    free_seats = [s for s in seats if s not in taken_seats]

    return {"seats": free_seats}



@router.post("/{event_id}/register")
def register(event_id: str, payload: dict, db: SessionDep):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if event.status != "published":
        raise HTTPException(status_code=400, detail="Event is not published")

    client = EventsProviderClient()
    result = client.register(event_id, payload)

    registration = Registration(
        id=result["ticket_id"],
        event_id=event_id,
        first_name=payload["first_name"],
        last_name=payload["last_name"],
        email=payload["email"],
        seat=payload["seat"]
    )
    db.add(registration)

    event.number_of_visitors += 1
    db.commit()

    return result


@router.delete("/{event_id}/unregister/{ticket_id}")
def unregister(event_id: str, ticket_id: str, db: SessionDep):
    registration = db.query(Registration).filter(
        Registration.id == ticket_id,
        Registration.event_id == event_id
    ).first()

    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")

    client = EventsProviderClient()
    client.unregister(event_id, ticket_id)

    db.delete(registration)

    event = db.query(Event).filter(Event.id == event_id).first()
    if event:
        event.number_of_visitors -= 1

    db.commit()

    return {"status": "ok"}
