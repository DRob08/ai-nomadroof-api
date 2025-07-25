# routers/receipts.py
from fastapi import APIRouter, HTTPException, Query, Response
from typing import Optional
from fastapi.responses import StreamingResponse, JSONResponse
from models.receipt_model import ReceiptModel
from services.receipt_service import get_receipt_data_by_booking_and_email
from jinja2 import Environment, FileSystemLoader, select_autoescape
#from weasyprint import HTML
import io
import os

router = APIRouter(prefix="/receipts", tags=["receipts"])

# Set up Jinja2 environment
template_env = Environment(
    loader=FileSystemLoader("templates"),  # folder where your HTML template is
    autoescape=select_autoescape(['html', 'xml'])
)

@router.get("/", response_model=Optional[ReceiptModel])
def get_receipt(booking_id: str = Query(...), email: str = Query(...)):
    receipt = get_receipt_data_by_booking_and_email(booking_id, email)
    if not receipt:
        return JSONResponse(content=None, status_code=200)
    return receipt



@router.get("/pdf", response_class=StreamingResponse)
def get_receipt_pdf(booking_id: str = Query(...), email: str = Query(...)):
    receipt = get_receipt_data_by_booking_and_email(booking_id, email)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found.")

    # Load the template and render it with receipt data
    template = template_env.get_template("receipt_template.html")
    html_content = template.render(receipt.dict())
