from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class BookingmModel(BaseModel):
    # Booking details
    post_id: int
    post_date: datetime
    post_title: str
    booking_status: str
    booking_invoice_no: Optional[str] = None

    # User details
    user_id: int
    user_login: str
    first_name: str
    user_email: str

    # Booking dates (stored as strings in DB, but can be changed to `date` if parsed)
    check_in: str
    check_out: str

    # Owner details
    owner_id: int
    owner_email: str
    owneralias: str

    # Property info (can be null if property doesn't exist)
    property_id: Optional[int] = None
    property_name: Optional[str] = None

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
