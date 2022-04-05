from sqlalchemy.orm import Session

import models


def get_conference_seats(db: Session):
    return db.query(models.ConferenceSeats)
