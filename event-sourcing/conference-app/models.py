from sqlalchemy import Column, Integer, String

from database import Base


class ConferenceSeats(Base):
    __tablename__ = "conference_seats"
    date = Column(String, primary_key=True)
    booked_seats = Column(Integer)
