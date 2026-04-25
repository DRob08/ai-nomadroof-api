from services.db_service import fetch_all
from datetime import datetime
import json


def format_author_name(full_name: str) -> str:
    if not full_name:
        return "Anonymous"
    parts = full_name.strip().split()
    if len(parts) == 1:
        return parts[0]
    return f"{parts[0]} {parts[1][0]}."


def format_review_date(date_val) -> str:
    try:
        if isinstance(date_val, str):
            date_val = datetime.strptime(date_val, "%Y-%m-%d %H:%M:%S")
        return date_val.strftime("%B %Y")
    except Exception:
        return str(date_val)


def parse_rating(raw: str):
    if not raw:
        return None, None
    try:
        data = json.loads(raw)
        overall = int(data.get("rating")) if data.get("rating") is not None else None
        breakdown = {
            "accuracy": data.get("accuracy"),
            "communication": data.get("communication"),
            "cleanliness": data.get("cleanliness"),
            "location": data.get("location"),
            "check_in": data.get("check_in"),
            "value": data.get("value"),
        }
        return overall, breakdown
    except Exception:
        return None, None


def get_legacy_reviews(property_name: str) -> dict:
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

    post_ids = [row["ID"] for row in matched_posts]
    matched_room_titles = [row["post_title"] for row in matched_posts]
    placeholders = ", ".join(["%s"] * len(post_ids))

    reviews_query = f"""
        SELECT
            c.comment_ID,
            c.comment_author,
            c.comment_date,
            c.comment_content,
            p.post_title AS room_title,
            cm.meta_value AS rating
        FROM wp_comments c
        INNER JOIN wp_posts p ON c.comment_post_ID = p.ID
        LEFT JOIN wp_commentmeta cm
            ON cm.comment_id = c.comment_ID
            AND cm.meta_key = 'review_stars'
        WHERE
            c.comment_post_ID IN ({placeholders})
            AND c.comment_approved = '1'
            AND p.post_type = 'estate_property'
            AND c.comment_content != ''
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

    shaped_reviews = []
    ratings = []

    for row in raw_reviews:
        overall, breakdown = parse_rating(row["rating"])
        if overall is not None:
            ratings.append(overall)

        shaped_reviews.append({
            "author": format_author_name(row["comment_author"]),
            "date": format_review_date(row["comment_date"]),
            "rating": overall,
            "rating_breakdown": breakdown,
            "content": row["comment_content"],
        })

    average_rating = round(sum(ratings) / len(ratings), 1) if ratings else None

    return {
        "property_searched": property_name,
        "matched_rooms": matched_room_titles,
        "total_reviews": len(shaped_reviews),
        "average_rating": average_rating,
        "reviews": shaped_reviews,
        "status": "ok"
    }
