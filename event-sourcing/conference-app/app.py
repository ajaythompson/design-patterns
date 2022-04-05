from datetime import datetime

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

import models
from conference import ConferenceController, KafkaBookingEventLogger
from database import SessionLocal, engine
from schemas import BookingEvent, BookingStatus, ConferenceSeats

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


bootstrap_servers = ["broker:29092"]
booking_topic = "bookings"
event_logger = KafkaBookingEventLogger(
    bootstrap_servers=bootstrap_servers, topic=booking_topic
)
conference = ConferenceController(max_seats=100, event_logger=event_logger)


@app.post("/book-seats")
async def book_conference_seats(
    booking_event: BookingEvent,
    db: Session = Depends(get_db),
) -> BookingStatus:
    if booking_event.timestamp is None:
        booking_event.timestamp = datetime.now().timestamp()
    return conference.book_seats(db=db, booking_event=booking_event)


@app.get("/available-seats")
async def get_available_seats(
    db: Session = Depends(get_db),
) -> ConferenceSeats:
    return conference.get_seats(db)
