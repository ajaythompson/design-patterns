import io
import json
from abc import ABC, abstractmethod
from typing import List

from kafka import KafkaProducer
from sqlalchemy.orm import Session

import crud
from schemas import BookingEvent, BookingStatus, ConferenceSeats, Status


class BookingEventLogger(ABC):
    @abstractmethod
    def add_event(self, booking_event: BookingEvent) -> None:
        pass


class KafkaBookingEventLogger(BookingEventLogger):

    def __init__(self, bootstrap_servers: List[str], topic: str) -> None:
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.kafka_producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda booking_event: json.dumps(booking_event.dict()).encode('utf-8'),
        )

    def add_event(self, booking_event: BookingEvent) -> None:
        return self.kafka_producer.send(self.topic, booking_event)


class ConferenceController(ABC):
    def __init__(
        self, max_seats: int, event_logger: BookingEventLogger
    ) -> None:
        self.event_logger = event_logger
        self.max_seats = max_seats

    def book_seats(
        self, db: Session, booking_event: BookingEvent
    ) -> BookingStatus:
        seats = self.get_seats(db)
        booked_seats = 0
        if seats:
            booked_seats = seats.booked_seats
        if booking_event.number_of_seats + booked_seats > self.max_seats:
            return BookingStatus(
                description="Max seats exceeded", status=Status.FAILED
            )
        else:
            self.event_logger.add_event(booking_event)
            return BookingStatus(
                description=f"Booked {booking_event.number_of_seats}"
                " successfully!",
                status=Status.SUCCESS,
            )

    def get_seats(self, db: Session) -> ConferenceSeats:
        return crud.get_conference_seats(db).first()
