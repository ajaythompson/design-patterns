import logging
from abc import ABC
from dataclasses import dataclass
from typing import Callable

logging.basicConfig(level=logging.INFO)


@dataclass
class Conference(ABC):
    max_seats: int
    get_booked_seats: Callable[[], int]
    book_seats: Callable[[int], None]

    def book_conference_seats(self, number_of_seats: int) -> bool:
        if number_of_seats + self.get_booked_seats() <= self.max_seats:
            self.book_seats(number_of_seats)
            logging.info(f"{number_of_seats} seats booked.")
            return True
        else:
            logging.info("Sorry! All bookings closed.")
            return False
