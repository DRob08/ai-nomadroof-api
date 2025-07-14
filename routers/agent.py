# routers/agent.py
from fastapi import APIRouter, HTTPException, Query
from routers.bookings import get_bookings
from services.ai_service import ask_gpt  # 👈 new import
from services.property_service import get_available_properties  
from models.property_model import PropertyModel
from models.insight_request_model import InsightRequest
from services.faq_service import find_answer_from_faq
import math
from utils.property_utils import properties_near_universities, get_university_summary
import json
import os
router = APIRouter()

#PUCP_COORDS = (-12.0685, -77.0796)  # Coordinates for PUCP in Lima

# UNIVERSITIES_IN_LIMA = {
#     "PUCP": (-12.0685, -77.0796),
#     "Universidad de Lima": (-12.0870, -76.9717),
#     "Universidad Nacional Mayor de San Marcos": (-12.0586, -77.0793),
#     "UPC Monterrico": (-12.1152, -76.9731),
#     "Universidad del Pacífico": (-12.0891, -77.0365)
# }

# SENSITIVE_KEYWORDS = [
#     "address", "exact location", "coordinates", "latitude", "longitude", "who owns", "who rented",
#     "email", "phone", "personal info", "owner name", "contact info"
# ]

universities_in_lima = json.loads(os.getenv("UNIVERSITIES_IN_LIMA", "{}"))
sensitive_keywords = json.loads(os.getenv("SENSITIVE_KEYWORDS", "[]"))

def is_sensitive_question(question: str) -> bool:
    lowered = question.lower()
    return any(keyword in lowered for keyword in sensitive_keywords)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

# def properties_near_universities(properties, university_coords, radius_km=5.0):
#     results = {}
#     for name, coords in university_coords.items():
#         nearby = []
#         for p in properties:
#             try:
#                 lat = float(p.property_latitude)
#                 lon = float(p.property_longitude)
#                 distance = haversine(lat, lon, coords[0], coords[1])
#                 if distance <= radius_km:
#                     nearby.append((p, round(distance, 2)))
#             except (TypeError, ValueError):
#                 continue
#         results[name] = nearby
#     return results

def is_true(val):
    return str(val).strip().lower() in ("true", "1", "yes")


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
        
        # Check for sensitive content
        if is_sensitive_question(question):
            return {"answer": "Your question contains sensitive content and cannot be processed."}
        
         # Try to answer using the FAQ first
        faq_answer = find_answer_from_faq(question)
        if faq_answer:
            return {"answer": faq_answer}

        # Identify properties close to PUCP (within 5 km)
        #nearby_pucp = properties_near_location(properties, PUCP_COORDS, radius_km=10.0)
        #near_summary = f"{len(nearby_pucp)} properties are located within 5km of PUCP."

        # Identify properties close to major Lima universities (within 5km)
        universities_proximity = properties_near_universities(properties, universities_in_lima, radius_km=10.0)
        near_summary = get_university_summary(universities_proximity, 10.0)

        # near_summary_lines = []
        # for uni_name, nearby_props in universities_proximity.items():
        #     near_summary_lines.append(f"{len(nearby_props)} properties are within 10km of {uni_name}.")
        # near_summary = "\n".join(near_summary_lines)

        # formatted_lines = []
        # for p in properties[:15]:
        #     district = (p.property_district or "").strip().title() or "N/A"
        #     city = (p.property_state or "").strip().title() or "Lima"
        #     country = (p.property_country or "").strip().title() or "Peru"

        #     formatted_line = (
        #         "'{title}' in {district}, {city}, {country} — {price}/mo, "
        #         "{rooms} rooms, Cancellation: {cancellation}. "
        #         "Amenities: {amenities}"
        #         "View Listing: https://www.nomadroof.com/properties/{url}"
        #     ).format(
        #         title=p.post_title,
        #         district=district,
        #         city=city,
        #         country=country,
        #         price=p.property_price_per_month or p.property_price or "N/A",
        #         rooms=p.property_bedrooms or "N/A",
        #         cancellation=p.cancellation_policy or "N/A",
     
        #         available_days=p.property_available_days or "N/A",
                
        #         amenities=", ".join(filter(None, [
        #             'Electricity' if p.electricity_included else None,
        #             'Pool' if p.pool else None,
        #             'Water' if p.water_included else None,
        #             'Gym' if p.gym else None,
        #             'Heating' if p.heating else None,
        #             'Hot Tub' if p.hot_tub else None,
        #             'A/C' if p.air_conditioning else None,
        #             'Parking' if p.free_parking_on_premises else None,
        #             'Desk' if p.desk else None,
        #             'Hangers' if p.hangers else None,
        #             'Closet' if p.closet else None,
        #             'Iron' if p.iron else None
        #         ])),
        #         url=p.half_property_url or ""
                
        #     )
        #     formatted_lines.append(formatted_line)

        # formatted = "\n".join(formatted_lines)

        formatted_lines = []
        for p in properties[:15]:
            district = (p.property_district or "").strip().title() or "N/A"
            city = (p.property_state or "").strip().title() or "Lima"
            country = (p.property_country or "").strip().title() or "Peru"

            amenities = ", ".join(filter(None, [
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
                'Washer' if p.washer else None,
                'Iron' if p.iron else None
            ])) or "None"

            formatted_line = (
                f"Title: {p.post_title}\n"
                f"Location: {district}, {city}, {country}\n"
                f"Price: {p.property_price_per_month or p.property_price or 'N/A'}/mo\n"
                f"Rooms: {p.property_bedrooms or 'N/A'}\n"
                f"Cancellation: {p.cancellation_policy or 'N/A'}\n"
                f"Amenities: {amenities}\n"
                f"View Listing: https://www.nomadroof.com/properties/{p.half_property_url or ''}\n"
            )

            formatted_lines.append(formatted_line)

        formatted = "\n".join(formatted_lines)


        formatted_props = []
        for p in properties:
            formatted_props.append({
                "title": p.post_title,
                "location": {
                    "district": (p.property_district or "").strip().title(),
                    "city": (p.property_state or "").strip().title() or "Lima",
                    "country": (p.property_country or "").strip().title() or "Peru"
                },
                "price": float(p.property_price_per_month or p.property_price or 0),
                "rooms": int(p.property_bedrooms or 0),
                "cancellation": p.cancellation_policy or "N/A",
                "amenities": list(filter(None, [
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
                    'Washer' if p.washer else None,
                    'Iron' if p.iron else None
                ])),
                "url": f"https://www.nomadroof.com/properties/{p.half_property_url or ''}"
            })

        formatted_json = json.dumps(formatted_props, indent=2)

        # messages = [
        #     {
        #         "role": "system",
        #         "content": (
        #             "You are a real estate analyst. NEVER mention or infer personal data, exact addresses, coordinates, or individual identities. "
        #             "Only give generalized, anonymized insights using cities, districts, prices, and amenities. "
        #             "If referencing or listing any specific property, you must always include the full property info line exactly as provided, including the View Listing link."
        #         )
        #     },
        #     {
        #         "role": "user",
        #         "content": (
        #             f"Below is a list of property listings. Each includes location, price, availability, amenities, and a 'View Listing' URL.\n\n"
        #             f"IMPORTANT: When referencing properties in your answer, copy and paste the **full line** exactly, including the View Listing URL.\n\n"
        #             f"--- PROPERTY LISTINGS START ---\n\n"
        #             f"{formatted}\n\n"
        #             f"--- PROPERTY LISTINGS END ---\n\n"
        #             f"Nearby university info: {near_summary}\n\n"
        #             f"Now, based only on this data, answer the following user question:\n\n{question}"
        #         )
        #     }
        # ]
        #print(formatted_json)

        messages = [
        {
            "role": "system",
            "content": (
                    "You are a helpful real estate assistant. Only answer questions related to Nomadroof Properties listings, housing, amenities, neighborhoods, or nearby universities. "
                    "If the user asks a question unrelated to real estate (e.g., math, general trivia), politely respond that you're only able to assist with Nomadroof network properties questions. "
                    "Only use the provided JSON data. Do not assume or fabricate information.Do not mention the data source or data format (like JSON) in your response. "
                    "Use the title and view listing link to reference properties. "

                    "Important: Be strict and logical in applying numeric filters. "
                    "If a user says 'under X', only return properties with price < X. "
                    "If a user says 'X or less', return properties with price <= X. "
                    "For example, if the user says 'under 400', exclude properties priced at 400 or more. "
                    "Do not round, approximate, or loosely interpret numeric values."

                    "**If the user's question is a filter-based query** (e.g., price under a certain amount, must include specific amenities, must be near a university), "
                    "**respond with a JSON array of matching property objects**, each with: `title`, `location`, `price`, `rooms`, `amenities`, and `url`. "
                    "Otherwise, respond with a regular natural language answer using the property data to support your response."

                  
                )
            },
        {
            "role": "user",
            "content": (
                f"Here is a list of property listings in JSON format:\n\n"
                f"{formatted_json}\n\n"
                f"Nearby university info: {near_summary}\n\n"
                f"Now, based only on this data, answer the following question:\n\n{question}"
            )
        }
      ]

        #print(formatted)
        answer = ask_gpt(messages)
        #return {"answer": answer}
      
        return {
            "answer": answer,
            "university_proximity": {
                uni: [dict(
                    post_title=p.post_title,
                    distance_km=dist
                ) for p, dist in prop_list]
                for uni, prop_list in universities_proximity.items()
            }
        }


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
    

@router.get("/faq-match")
def faq_match_endpoint(q: str = Query(..., description="User's question")):
    answer = find_answer_from_faq(q)

    if answer:
        return {
            "answer": answer
        }
    else:
        return {
            "matched_question": None,
            "answer": "Sorry, I couldn’t find an answer. Would you like help from a human?",
        }




