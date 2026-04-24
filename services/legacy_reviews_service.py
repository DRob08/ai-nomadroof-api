

from services.db_service import fetch_all
from datetime import datetime


def format_author_name(full_name: str) -> str:
    """
    Formats reviewer name for display.
    "John Smith" -> "John S."
    "Maria"      -> "Maria"
    """
    if not full_name:
        return "Anonymous"
    parts = full_name.strip().split()
    if len(parts) == 1:
        return parts[0]
    return f"{parts[0]} {parts[1][0]}."


def format_review_date(date_val) -> str:
    """
    Formats comment_date for display.
    datetime obj or string -> "March 2023"
    """
    try:
        if isinstance(date_val, str):
            date_val = datetime.strptime(date_val, "%Y-%m-%d %H:%M:%S")
        return date_val.strftime("%B %Y")
    except Exception:
        return str(date_val)


def get_legacy_reviews(property_name: str) -> dict:
    """
    Given a property name from the new platform,
    fuzzy-matches against old WP post_titles to find all
    associated rooms, then retrieves all approved reviews.
    """

    # --------------------------------------------------
    # STEP 1: Find all matching WP room/property post IDs
    # --------------------------------------------------
    match_query = """
        SELECT ID, post_title
        FROM wp_posts
        WHERE post_type = 'estate_property'
          AND post_status = 'publish'
          AND post_title LIKE %s
    """
    matched_posts = fetch_all(match_query, params=(f"%{property_name}%",))

    if not matched_posts:
        return {
            "property_searched": property_name,
            "matched_rooms": [],
            "total_reviews": 0,
            "average_rating": None,
            "reviews": [],
            "status": "no_match"
        }

    # Extract all matched post IDs
    post_ids = [row["ID"] for row in matched_posts]
    matched_room_titles = [row["post_title"] for row in matched_posts]

    # Build IN clause placeholders safely e.g. %s, %s, %s
    placeholders = ", ".join(["%s"] * len(post_ids))

    # --------------------------------------------------
    # STEP 2: Fetch all approved reviews for those posts
    # --------------------------------------------------
    reviews_query = f"""
        SELECT
            c.comment_ID,
            c.comment_author,
            c.comment_date,
            c.comment_content,
            p.post_title AS room_title,
            cm.meta_value AS rating
        FROM wp_comments c
        INNER JOIN wp_posts p
            ON c.comment_post_ID = p.ID
        LEFT JOIN wp_commentmeta cm
            ON cm.comment_id = c.comment_ID
            AND cm.meta_key = 'review_stars'
        WHERE
            c.comment_post_ID IN ({placeholders})
            AND c.comment_approved = '1'
            AND p.post_type = 'estate_property'
        ORDER BY c.comment_date DESC
    """
    raw_reviews = fetch_all(reviews_query, params=tuple(post_ids))

    if not raw_reviews:
        return {
            "property_searched": property_name,
            "matched_rooms": matched_room_titles,
            "total_reviews": 0,
            "average_rating": None,
            "reviews": [],
            "status": "no_reviews"
        }

    # --------------------------------------------------
    # STEP 3: Shape reviews for response
    # --------------------------------------------------
    shaped_reviews = []
    ratings = []

    for row in raw_reviews:
        rating = None
        if row["rating"] is not None:
            try:
                rating = int(float(row["rating"]))
                ratings.append(rating)
            except (ValueError, TypeError):
                pass

        shaped_reviews.append({
            "author": format_author_name(row["comment_author"]),
            "date": format_review_date(row["comment_date"]),
            "rating": rating,
            "content": row["comment_content"],
        })

    average_rating = round(sum(ratings) / len(ratings), 1) if ratings else None

    return {
        "property_searched": property_name,
        "matched_rooms": matched_room_titles,   # useful for debugging on your end
        "total_reviews": len(shaped_reviews),
        "average_rating": average_rating,
        "reviews": shaped_reviews,
        "status": "ok"
    }