from fastapi import APIRouter
from typing import List
from models.booking_model import BookingmModel  # <-- make sure this import path matches your project structure
from services.db_service import fetch_all


router = APIRouter()

@router.get("/bookings", response_model=List[BookingmModel])
def get_bookings():
    query = """
    SELECT wp_posts.post_date, 
        wp_posts.post_title, 
        m2.meta_value as check_in, 
        m4.meta_value as check_out, 
        m1.meta_value as booking_status, 
        u1.id as user_id, 
        u1.user_login, 
        wp_posts.ID as post_id, 
        um.meta_value as first_name, 
        u1.user_email, 
        m3.meta_value as owner_id, 
        uown.user_email as owner_email, 
        m5.meta_value as property_id, 
        m6.meta_value as booking_invoice_no,
        uown.user_nicename as owneralias,
        b.post_title as property_name
        FROM wp_posts 
        INNER JOIN wp_postmeta m1 ON ( wp_posts.ID = m1.post_id )
        INNER JOIN wp_postmeta m2 ON ( wp_posts.ID = m2.post_id )
        INNER JOIN wp_postmeta m3 ON ( wp_posts.ID = m3.post_id )
        INNER JOIN wp_postmeta m4 ON ( wp_posts.ID = m4.post_id )
        INNER JOIN wp_users u1 ON(wp_posts.post_author = u1.ID)
        INNER JOIN wp_usermeta um ON(u1.ID = um.user_id)
        INNER JOIN wp_users uown ON(m3.meta_value = uown.id)
        INNER JOIN wp_postmeta m5 ON ( wp_posts.ID = m5.post_id )
        INNER JOIN wp_posts b ON ( m5.meta_value = b.ID )
        LEFT JOIN wp_postmeta m6 ON ( wp_posts.ID = m6.post_id AND m6.meta_key = 'booking_invoice_no' )
        WHERE wp_posts.post_type = 'wpestate_booking'
        AND wp_posts.post_status = 'publish'
        AND ( m1.meta_key = 'booking_status' AND m1.meta_value IN ('pending', 'waiting', 'confirmed', 'canceled') )
        AND ( m2.meta_key = 'booking_from_date' )
        AND ( m3.meta_key = 'owner_id' AND m3.meta_value <> u1.id )
        AND ( um.meta_key = 'first_name' AND LENGTH(um.meta_value) > 0 )
        AND ( m4.meta_key = 'booking_to_date' )
        AND ( m5.meta_key = 'booking_id' )
        AND wp_posts.post_date >= '2022-01-01'
        ORDER BY wp_posts.post_date DESC;
    """

    results = fetch_all(query)

    # Transform into Booking model list
    bookings = [BookingmModel(**row) for row in results]
    return bookings
