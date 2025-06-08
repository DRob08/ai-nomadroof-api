from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from services.email_service import send_contact_email

router = APIRouter()

class ContactFormData(BaseModel):
    name: str
    email: EmailStr
    whatsapp: str
    message: str

@router.post("/contact")
async def submit_contact_form(data: ContactFormData):
    try:
        send_contact_email(
            name=data.name,
            email=data.email,
            whatsapp=data.whatsapp,
            message_body=data.message,
        )
        return {"message": "Contact form submitted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")
