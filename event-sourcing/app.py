import logging

from fastapi import FastAPI

from conference import Conference
from models import BookingStatus, Status, Seats, BookingHistory

logging.basicConfig(level=logging.INFO)


app = FastAPI()

booking_log = []


def get_booked_seats() -> int:
    return sum(booking_log, 0)


def book_seats(number_of_seats: int):
    booking_log.append(number_of_seats)


conference = Conference(
    max_seats=100, get_booked_seats=get_booked_seats, book_seats=book_seats
)


@app.post("/book-seats")
async def book_conference_seats(seats: Seats):
    number_of_seats = seats.number_of_seats
    book_seats_status = conference.book_conference_seats(number_of_seats)
    print(book_seats_status)
    if book_seats_status:
        return BookingStatus(
            desciption=f"Booked {number_of_seats} seats successfully.",
            status=Status.SUCCESS,
        )
    else:
        return BookingStatus(
            desciption="Failed to book seats!", status=Status.FAILED
        )


@app.get("/available-seats")
async def get_available_seats():
    return get_booked_seats()


@app.get("/booking-history")
async def get_available_seats():
    return BookingHistory(history=booking_log)