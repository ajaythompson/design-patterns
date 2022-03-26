from enum import Enum
from typing import List

from pydantic import BaseModel


class Status(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class BookingStatus(BaseModel):
    desciption: str
    status: Status

class Seats(BaseModel):
    number_of_seats: int

class BookingHistory(BaseModel):
    history: List[int]