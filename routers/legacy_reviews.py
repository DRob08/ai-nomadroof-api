# routers/legacy_reviews_router.py

from fastapi import APIRouter, Query, HTTPException
from services.legacy_reviews_service import get_legacy_reviews

router = APIRouter(
    prefix="/legacy-reviews",
    tags=["Legacy Reviews"]
)


@router.get("/")
def fetch_legacy_reviews(
    property_name: str = Query(
        ...,
        description="Property name from the new platform to match against old WP DB",
        min_length=3
    )
):
    """
    Retrieves reviews from the old WordPress database for a given property.

    Fuzzy-matches the property_name against old WP room post_titles,
    aggregates all reviews across matched rooms, and returns them
    shaped for display on the new platform.
    """
    if not property_name or len(property_name.strip()) < 3:
        raise HTTPException(
            status_code=400,
            detail="property_name must be at least 3 characters"
        )

    result = get_legacy_reviews(property_name.strip())

    if result["status"] == "no_match":
        raise HTTPException(
            status_code=404,
            detail=f"No properties found in legacy DB matching '{property_name}'"
        )

    return result