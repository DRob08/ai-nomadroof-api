from fastapi import APIRouter, Query
from services.property_service import get_available_properties, get_exclusive_properties
from models.property_model import PropertyModel
from typing import List
from typing import Optional

router = APIRouter()

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
    filters = {
        "city": city,
        "district": district,
        "dates": dates,
        "startDate": startDate,
        "endDate": endDate,
        "priceRange": priceRange,
        "districtLat": districtLat,
        "districtLng": districtLng,
        "minPrice": minPrice,
        "maxPrice": maxPrice
        }
    print(filters)
    return get_available_properties(filters)

@router.get("/exclusive-properties", response_model=List[PropertyModel])
def list_exclusive_properties():
    return get_exclusive_properties()

