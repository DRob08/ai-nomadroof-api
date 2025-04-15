# routers/agent.py
from fastapi import APIRouter, HTTPException
from routers.bookings import get_bookings
from openai import OpenAI
from dotenv import load_dotenv
from config import settings
import os
import requests

router = APIRouter()

# Load .env and initialize OpenAI client
load_dotenv()
client = OpenAI(api_key=settings.OPENAI_API_KEY)

@router.get("/booking-insights")
def get_booking_insights():
    try:
        bookings = get_bookings()

        if not bookings:
            return {"insights": "No booking data available."}

        formatted = "\n".join([
            f"{b.first_name} ({b.user_login}) booked '{b.property_name}' "
            f"from {b.check_in} to {b.check_out} — Status: {b.booking_status}"
            for b in bookings[:20]
        ])

        prompt = (
            f"Analyze the following booking data:\n\n{formatted}\n\n"
            "Give insights on trends, cancellations, property popularity, or guest behavior.Which property had the most bookings in March"
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a data analyst specializing in booking insights."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=350,
            temperature=0.7
        )

        return {"insights": response.choices[0].message.content.strip()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/my-ip")
def get_ip():
    return requests.get("https://api.ipify.org?format=json").json()