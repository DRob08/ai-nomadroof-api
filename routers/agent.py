# routers/agent.py
from fastapi import APIRouter, HTTPException
from routers.bookings import get_bookings
from services.ai_service import ask_gpt  # 👈 new import
from services.property_service import get_available_properties  
from models.property_model import PropertyModel
from models.insight_request_model import InsightRequest
import math

router = APIRouter()

PUCP_COORDS = (-12.0685, -77.0796)  # Coordinates for PUCP in Lima

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def properties_near_location(properties, target_coords, radius_km=5.0):
    nearby = []
    for p in properties:
        try:
            lat = float(p.property_latitude)
            lon = float(p.property_longitude)
            distance = haversine(lat, lon, target_coords[0], target_coords[1])
            print(distance)
            print(radius_km)
            if distance <= radius_km:
                nearby.append((p, round(distance, 2)))
        except (TypeError, ValueError):
            continue
    return nearby

@router.post("/property-insight")
def property_insight(request: InsightRequest):
    try:
        properties = request.properties
        question = request.question

        if not properties:
            return {"answer": "No property data provided."}

        # Identify properties close to PUCP (within 5 km)
        nearby_pucp = properties_near_location(properties, PUCP_COORDS, radius_km=10.0)
        near_summary = f"{len(nearby_pucp)} properties are located within 5km of PUCP."

        formatted_lines = []
        for p in properties[:100]:
            district = (p.property_district or "").strip().title() or "N/A"
            city = (p.property_state or "").strip().title() or "Lima"
            country = (p.property_country or "").strip().title() or "Peru"

            formatted_line = (
                "'{title}' in {district}, {city}, {country} — {price}/mo, "
                "{rooms} rooms, Cancellation: {cancellation}. "
                "Available for: {available_days} days. Amenities: {amenities}"
            ).format(
                title=p.post_title,
                district=district,
                city=city,
                country=country,
                price=p.property_price_per_month or p.property_price or "N/A",
                rooms=p.property_bedrooms or "N/A",
                cancellation=p.cancellation_policy or "N/A",
                available_days=p.property_available_days or "N/A",
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
            formatted_lines.append(formatted_line)

        formatted = "\n".join(formatted_lines)

        messages = [
            {"role": "system", "content": (
                "You are a helpful real estate analyst. "
                "Do not repeat or expose any exact addresses or geographic coordinates. "
                "Summarize based on city, district, amenities, and pricing only."
            )},
            {"role": "user", "content": (
                f"Here are property listings:\n\n{formatted}\n\n"
                f"Additional info: {near_summary}\n\n"
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

        formatted_lines = []
        for p in properties[:20]:
            # Sanitize and normalize values
            district = (p.property_district or "").strip() or "N/A"
            country = (p.property_country or "").strip().title() or "N/A"
            address= (p.property_address or "").strip().title() or "N/A"
            city = "Lima"  # hardcoded for now; extract dynamically if needed

            print(f"[DEBUG] Property: '{p.post_title}', District: {district}, Country: {country}")

            formatted_line = "'{title}' in {district}, {city}, {country} — {price} USD/Monthly, Type: {size}, Rooms: {rooms}, Address: {property_address}, Amenities: {amenities}".format(
                            title=p.post_title,
                            district=district,
                            city=city,
                            country=country,
                            price=p.property_price,
                            size=p.property_size,
                            rooms=p.property_rooms,
                            property_address=p.property_address,
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

            formatted_lines.append(formatted_line)

        formatted = "\n".join(formatted_lines)

        messages = [
            {"role": "system", "content": "You are a real estate analyst. Your job is to analyze available property listings."},
            {"role": "user", "content": (
                f"Here are some available properties:\n\n{formatted}\n\n"
                "Which districts or areas have the most properties? What is the price range? Any interesting trends?"
            )}
        ]

        insights = ask_gpt(messages)
        return {"insights": insights}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


