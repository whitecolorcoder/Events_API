from datetime import datetime
from sqlalchemy.orm import Session

from src.services.events_provider_client import EventsProviderClient
from src.database.models import Place, Event, SyncMetadata


def parse_dt(value: str) -> datetime:
    """Convert ISO datetime string from API to Python datetime"""
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class SyncService:
    def __init__(self, db: Session):
        self.db = db
        self.client = EventsProviderClient()

    def get_or_create_metadata(self) -> SyncMetadata:
        metadata = self.db.query(SyncMetadata).first()

        if metadata is None:
            metadata = SyncMetadata(
                id=1,
                last_sync_time=datetime(2000, 1, 1),
                last_changed_at=datetime(2000, 1, 1)
            )
            self.db.add(metadata)
            self.db.commit()
            self.db.refresh(metadata)

        return metadata

    def sync(self):
        metadata = self.get_or_create_metadata()

        changed_at = metadata.last_changed_at.date().isoformat()

        events_data = self.client.get_all_events(changed_at)

        existing_places = {str(p.id): p for p in self.db.query(Place).all()}
        existing_events = {str(e.id): e for e in self.db.query(Event).all()}

        max_changed_at = metadata.last_changed_at

        for item in events_data:
            place_data = item["place"]
            place_id = str(place_data["id"])

            # -------- PLACE --------

            if place_id in existing_places:
                place = existing_places[place_id]

                place.name = place_data["name"]
                place.city = place_data["city"]
                place.address = place_data["address"]
                place.seats_pattern = place_data["seats_pattern"]
                place.created_at = parse_dt(place_data["created_at"])
                place.changed_at = parse_dt(place_data["changed_at"])

            else:
                place = Place(
                    id=place_id,
                    name=place_data["name"],
                    city=place_data["city"],
                    address=place_data["address"],
                    seats_pattern=place_data["seats_pattern"],
                    created_at=parse_dt(place_data["created_at"]),
                    changed_at=parse_dt(place_data["changed_at"])
                )

                self.db.add(place)
                existing_places[place_id] = place

            # -------- EVENT --------

            event_id = str(item["id"])

            if event_id in existing_events:
                event = existing_events[event_id]

                event.name = item["name"]
                event.place_id = place_id
                event.event_time = parse_dt(item["event_time"])
                event.registration_deadline = parse_dt(item["registration_deadline"])
                event.status = item["status"]
                event.number_of_visitors = item["number_of_visitors"]
                event.created_at = parse_dt(item["created_at"])
                event.changed_at = parse_dt(item["changed_at"])
                event.status_changed_at = parse_dt(item["status_changed_at"])

            else:
                event = Event(
                    id=event_id,
                    name=item["name"],
                    place_id=place_id,
                    event_time=parse_dt(item["event_time"]),
                    registration_deadline=parse_dt(item["registration_deadline"]),
                    status=item["status"],
                    number_of_visitors=item["number_of_visitors"],
                    created_at=parse_dt(item["created_at"]),
                    changed_at=parse_dt(item["changed_at"]),
                    status_changed_at=parse_dt(item["status_changed_at"])
                )

                self.db.add(event)
                existing_events[event_id] = event

            # -------- MAX CHANGED_AT --------

            changed_at_item = parse_dt(item["changed_at"])

            if changed_at_item > max_changed_at:
                max_changed_at = changed_at_item

        # -------- METADATA UPDATE --------

        metadata.last_sync_time = datetime.utcnow()
        metadata.last_changed_at = max_changed_at

        self.db.commit()