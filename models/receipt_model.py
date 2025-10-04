# models/receipt_model.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReceiptModel(BaseModel):
    booking_id: str
    inv_no: str
    property_title: str
    property_address: str
    guest_full_name: str
    email: str
    monthly_fee: float
    total_paid: float
    service_fee: float
    invoice_date: str
    booking_paid_date: str
