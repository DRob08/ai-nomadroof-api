# routers/agent.py
from fastapi import APIRouter, HTTPException
from routers.bookings import get_bookings
from services.ai_service import ask_gpt  # 👈 new import
from services.property_service import get_available_properties  
from models.property_model import PropertyModel
from models.insight_request_model import InsightRequest

router = APIRouter()

@router.post("/property-insight")
def property_insight(request: InsightRequest):
    try:
        properties = request.properties
        question = request.question

        if not properties:
            return {"answer": "No property data provided."}

        # Format property data
        formatted = "\n".join([
            "'{title}' in {state}, {country} — {price}/mo, {rooms} rooms. Amenities: {amenities}".format(
                title=p.post_title,
                state=p.property_state or "Unknown",
                country=p.property_country or "Unknown",
                price=p.property_price_per_month or p.property_price or "N/A",
                rooms=p.property_bedrooms or "N/A",
                cancellation_policy = p.cancellation_policy or "N/A",
                amenities=", ".join(filter(None, [
                     'Electricity' if p.electricity_included else None,
                    'Pool' if p.pool else None,
                    'Water' if p.water_included else None,
                    'Gym' if p.gym else None,
                    'Heating' if p.heating else None,
                    'Hot Tub' if p.hot_tub else None,
                    'A/C' if p.air_conditioning else None,
                    'Parking' if p.free_parking_on_premises else None,
                    'Desk' if p.desk else None,
                    'Hangers' if p.hangers else None,
                    'Closet' if p.closet else None,
                    'Iron' if p.iron else None
                ]))
            )
            for p in properties[:30]  # Limit to 30 if needed
        ])

        messages = [
            {"role": "system", "content": "You are a helpful real estate analyst."},
            {"role": "user", "content": (
                f"Here are property listings:\n\n{formatted}\n\n"
                f"Now, answer the following question based on this data:\n\n{question}"
            )}
        ]

        answer = ask_gpt(messages)
        return {"answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/booking-insights")
def get_booking_insights():
    try:
        bookings = get_bookings()

        if not bookings:
            return {"insights": "No booking data available."}

        formatted = "\n".join([
    f"Booking #{b.post_id} | {b.first_name} ({b.user_login}) "
    f"booked '{b.property_name or 'Unknown Property'}' "
    f"from {b.check_in} to {b.check_out} — Status: {b.booking_status}\n"
    f"Post Title: {b.post_title} | Invoice: {b.booking_invoice_no or 'N/A'}\n"
    f"Owner: {b.owneralias} ({b.owner_email})\n"
    f"User Email: {b.user_email}\n"
    f"{'-'*60}"
    for b in bookings[:100]
])


        messages = [
            {"role": "system", "content": "You are a data analyst specializing in booking insights."},
            {"role": "user", "content": (
                f"Analyze the following booking data:\n\n{formatted}\n\n"
                "Give insights on trends, cancellations, property popularity, or guest behavior. "
                "Which property had the most bookings in March?"
            )}
        ]

        insights = ask_gpt(messages)
        return {"insights": insights}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/available-properties-insights")
def available_properties_insights():
    try:
        properties = get_available_properties({})  # You can pass filters later

        if not properties:
            return {"insights": "No available property data found."}

        formatted = "\n".join([
            "'{title}' in {state} — {price} USD/Monthly, Type: {size}, Rooms: {rooms}, Amenities: {amenities}".format(
                title=p.post_title,
                state=p.property_state,
                price=p.property_price,
                size=p.property_size,
                rooms=p.property_rooms,
                amenities=", ".join(filter(None, [
                    'Electricity' if p.electricity_included else None,
                    'Pool' if p.pool else None,
                    'Water' if p.water_included else None,
                    'Gym' if p.gym else None,
                    'Heating' if p.heating else None,
                    'Hot Tub' if p.hot_tub else None,
                    'A/C' if p.air_conditioning else None,
                    'Parking' if p.free_parking_on_premises else None,
                    'Desk' if p.desk else None,
                    'Hangers' if p.hangers else None,
                    'Closet' if p.closet else None,
                    'Iron' if p.iron else None
                ]))
            )
            for p in properties[:20]
        ])

        messages = [
            {"role": "system", "content": "You are a real estate analyst. Your job is to analyze available property listings."},
            {"role": "user", "content": (
                f"Here are some available properties:\n\n{formatted}\n\n"
                "Which cities have the most properties? What is the price range? Any interesting trends?"
            )}
        ]

        insights = ask_gpt(messages)
        return {"insights": insights}

    except Exception as e:
        raise HTTPException
