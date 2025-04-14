from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class Booking(BaseModel):
    post_date: datetime
    post_title: str

    check_in: str  # Can be changed to `date` if desired
    booking_status: str

    user_id: int
    user_login: str
    post_id: int
    first_name: str
    user_email: str

    owner_id: int
    owner_email: str
    check_out: str  # Can be changed to `date` if desired

    property_id: int
    owneralias: str
    property_name: str

    class Config:
        orm_mode = True

class BookingCreate(BaseModel):
    first_name: str
    user_login: str
    property_name: str
    check_in: date
    check_out: date
    booking_status: str

class BookingUpdate(BaseModel):
    check_in: Optional[date] = None
    check_out: Optional[date] = None
    booking_status: Optional[str] = None
