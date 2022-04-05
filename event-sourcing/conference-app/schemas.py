
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel


class Status(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class BookingStatus(BaseModel):
    description: str
    status: Status


class BookingEvent(BaseModel):
    timestamp: Optional[float] = None
    date: str
    number_of_seats: int

    @classmethod
    def get_avro_schema(cls) -> Dict[str, any]:
        return {
            "namespace": "bookingEvent.avro",
            "type": "record",
            "name": "BookingEvent",
            "fields": [
                {"name": "timestamp", "type": "float"},
                {"name": "number_of_seats", "type": "int"},
            ],
        }


class BookingHistory(BaseModel):
    history: List[BookingEvent]


class ConferenceSeats(BaseModel):
    conference_date: str
    booked_seats: int

    class Config:
        orm_mode = True


class BookingSnapshot(BaseModel):
    number_of_seats: int
