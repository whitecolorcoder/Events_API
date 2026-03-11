from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from src.database.base import Base


class Place(Base):
    __tablename__ = "place"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    seats_pattern: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    events: Mapped[list["Event"]] = relationship(
        back_populates="place",
        cascade="all, delete-orphan"
    )


class Event(Base):
    __tablename__ = "event"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    place_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("place.id"),
        nullable=False,
        index=True
    )

    event_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    registration_deadline: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    status: Mapped[str] = mapped_column(String(50), nullable=False)
    number_of_visitors: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    status_changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    place: Mapped["Place"] = relationship(back_populates="events")

    registrations: Mapped[list["Registration"]] = relationship(
        back_populates="event",
        cascade="all, delete-orphan"
    )



class Registration(Base):
    __tablename__ = "registration"

    id: Mapped[int] = mapped_column(primary_key=True)

    ticket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True
    )

    event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("event.id"),
        nullable=False,
        index=True
    )

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    seat: Mapped[str] = mapped_column(String(20), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    event: Mapped["Event"] = relationship(back_populates="registrations")


class SyncMetadata(Base):
    __tablename__ = "sync_metadata"

    id: Mapped[int] = mapped_column(primary_key=True)

    last_sync_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    last_changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
