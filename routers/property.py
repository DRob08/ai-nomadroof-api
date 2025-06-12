from fastapi import APIRouter, Query, HTTPException
from services.property_service import get_available_properties, get_exclusive_properties
from models.property_model import PropertyModel
from typing import List
from typing import Optional
from datetime import datetime

router = APIRouter()

import re

def parse_date_safe(date_str: Optional[str], field_name: str) -> Optional[str]:
    if not date_str:
        return None
    
    # If already in ISO format (YYYY-MM-DD), skip parsing
    if re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        return date_str
    
    # Try parsing MM/DD/YYYY (common on iPhone/mobile)
    try:
        dt = datetime.strptime(date_str, "%m/%d/%Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid date format for {field_name}: {date_str}. Expected YYYY-MM-DD or MM/DD/YYYY."
        )


@router.get("/properties", response_model=List[PropertyModel])
def list_properties(
    city: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    dates: Optional[str] = Query(None),
    startDate: Optional[str] = Query(None),
    endDate: Optional[str] = Query(None),
    priceRange: Optional[str] = Query(None),
    districtLat: Optional[float] = Query(None),
    districtLng: Optional[float] = Query(None),
    minPrice: Optional[float] = Query(None),
    maxPrice: Optional[float] = Query(None)
):
    normalized_start = parse_date_safe(startDate, "startDate")
    normalized_end = parse_date_safe(endDate, "endDate")

    filters = {
        "city": city,
        "district": district,
        "dates": dates,
        "startDate": normalized_start,
        "endDate": normalized_end,
        "priceRange": priceRange,
        "districtLat": districtLat,
        "districtLng": districtLng,
        "minPrice": minPrice,
        "maxPrice": maxPrice
    }

    return get_available_properties(filters)


@router.get("/exclusive-properties", response_model=List[PropertyModel])
def list_exclusive_properties():
    return get_exclusive_properties()

