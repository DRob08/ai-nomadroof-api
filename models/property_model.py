from pydantic import BaseModel
from typing import Optional

class PropertyModel(BaseModel):
    post_title: str
    half_property_url: str
    full_thumbnail_url: Optional[str]
    property_size: Optional[str]
    property_rooms: Optional[str]
    property_bedrooms: Optional[str]
    property_bathrooms: Optional[str]
    property_address: Optional[str]
    property_district: Optional[str] = None  # Default value makes it optional
    property_state: Optional[str]
    property_country: Optional[str]
    property_latitude: Optional[str]
    property_longitude: Optional[str]
    property_available_days: Optional[str]
    property_booking_dates: Optional[str]
    guest_no: Optional[str]
    property_price: Optional[str]
    property_price_per_month: Optional[str]
    uni_nearby: Optional[str]
    about_neighborhood: Optional[str]
    cancellation_policy: Optional[str]
    property_admin_area: Optional[str]
    owner_name: Optional[str]
    owner_first_name: Optional[str]
    bedroom_descr: Optional[str]

    # Updated to return actual booleans now
    electricity_included: Optional[bool]
    pool: Optional[bool]
    water_included: Optional[bool]
    gym: Optional[bool]
    heating: Optional[bool]
    hot_tub: Optional[bool]
    air_conditioning: Optional[bool]
    free_parking_on_premises: Optional[bool]
    desk: Optional[bool]
    hangers: Optional[bool]
    closet: Optional[bool]
    iron: Optional[bool]
    is_prop_featured: Optional[bool]
    washer: Optional[bool]
