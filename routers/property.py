from fastapi import APIRouter
from services.property_service import get_available_properties
from models.property_model import PropertyModel
from typing import List

router = APIRouter()

@router.get("/properties", response_model=List[PropertyModel])
def list_properties():
    return get_available_properties()

