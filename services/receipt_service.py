from services.db_service import fetch_all
from models.receipt_model import ReceiptModel
from typing import Optional
from datetime import datetime

def get_receipt_data_by_booking_and_email(booking_id: str, email: str) -> Optional[ReceiptModel]:
    print(f"🔍 Step 1: Fetching booking for ID: {booking_id}, Email: {email}")

    booking_sql = """
        SELECT 
            b.ID as booking_id,
            u1.user_email,
            m6.meta_value AS invoice_no,
            m5.meta_value AS property_id,
            m3.meta_value AS buyer_id
        FROM wp_posts b
        LEFT JOIN wp_postmeta m1 ON b.ID = m1.post_id AND m1.meta_key = 'booking_status'
        LEFT JOIN wp_postmeta m3 ON b.ID = m3.post_id AND m3.meta_key = 'buyer_id'
        LEFT JOIN wp_postmeta m5 ON b.ID = m5.post_id AND m5.meta_key = 'booking_id'
        LEFT JOIN wp_postmeta m6 ON b.ID = m6.post_id AND m6.meta_key = 'booking_invoice_no'
        LEFT JOIN wp_users u1 ON b.post_author = u1.ID
        WHERE b.ID = %s
          AND u1.user_email = %s
          AND m1.meta_value = 'confirmed'
          AND b.post_type = 'wpestate_booking'
          AND b.post_status = 'publish'
    """
    print("📄 Executing Booking SQL...")
    booking_result = fetch_all(booking_sql, (booking_id, email))

    if not booking_result:
        print("❌ No booking found.")
        return None

    booking_row = booking_result[0]
    print("✅ Booking Found:", booking_row)

    invno = booking_row['invoice_no']
    property_id = booking_row['property_id']
    buyer_id = booking_row['buyer_id']

    print(f"📦 Invoice No: {invno}, Property ID: {property_id}, Buyer ID: {buyer_id}")

    # Step 2: Fetch receipt info using invoice_no and property_id
    receipt_sql = """
        SELECT 
            wp_posts.post_date,
            wp_posts.post_title,
            m2.meta_value AS property_address,
            m1.meta_value AS about_neighborhood,
            m3.meta_value AS images_id,
            m4.meta_value AS image_path,
            m5.meta_value AS images_data,
            m6.meta_value AS monthly_fee,
            m7.meta_value AS total_paid,
            um.meta_value AS first_name,
            um2.meta_value AS last_name,
            m8.meta_value AS buyer_id,
            wp_posts.post_author,
            m9.meta_value AS invoice_date,
            mt.meta_value AS item_price_total,
            m10.meta_value AS property_country,
            msg.first_confirmation_date AS booking_paid_date  

        FROM wp_posts
        LEFT JOIN wp_postmeta m1 ON wp_posts.ID = m1.post_id AND m1.meta_key = 'about_neighborhood'
        LEFT JOIN wp_postmeta m2 ON wp_posts.ID = m2.post_id AND m2.meta_key = 'property_address'
        LEFT JOIN wp_postmeta m3 ON wp_posts.ID = m3.post_id AND m3.meta_key = '_thumbnail_id'
        LEFT JOIN wp_postmeta m4 ON m3.meta_value = m4.post_id AND m4.meta_key = '_wp_attached_file'
        LEFT JOIN wp_postmeta m5 ON m3.meta_value = m5.post_id AND m5.meta_key = '_wp_attachment_metadata'
        LEFT JOIN wp_postmeta m6 ON m6.post_id = %s AND m6.meta_key = 'month_price'
        LEFT JOIN wp_postmeta m7 ON m7.post_id = %s AND m7.meta_key = 'depozit_paid'
        LEFT JOIN wp_postmeta m8 ON m8.post_id = %s AND m8.meta_key = 'buyer_id'
        LEFT JOIN wp_postmeta m9 ON m9.post_id = %s AND m9.meta_key = 'purchase_date'
        LEFT JOIN wp_postmeta mt ON mt.post_id = %s AND mt.meta_key = 'item_price'
        LEFT JOIN wp_usermeta um ON m8.meta_value = um.user_id AND um.meta_key = 'first_name'
        LEFT JOIN wp_usermeta um2 ON m8.meta_value = um2.user_id AND um2.meta_key = 'last_name'
        LEFT JOIN wp_postmeta m10 ON wp_posts.ID = m10.post_id AND m10.meta_key = 'property_country'
        LEFT JOIN (
            SELECT 
                msgmeta.meta_value AS booking_id,
                MIN(msg.post_date_gmt) AS first_confirmation_date
            FROM wp_posts msg
            INNER JOIN wp_postmeta msgmeta 
                ON msg.ID = msgmeta.post_id 
                AND msgmeta.meta_key = 'booking_reference_id'
            WHERE msg.post_type = 'wpestate_message'
              AND msg.post_content LIKE '%%A booking was confirmed%%'
            GROUP BY msgmeta.meta_value
        ) msg ON msg.booking_id = %s
        WHERE wp_posts.post_type = 'estate_property'
          AND wp_posts.post_status = 'publish'
          AND wp_posts.ID = %s
    """

    print("📄 Executing Receipt SQL...")
    receipt_result = fetch_all(
        receipt_sql,
        (invno, invno, invno, invno, invno, booking_id, property_id)
    )

    if not receipt_result:
        print("❌ No receipt found.")
        return None

    row = receipt_result[0]
    print("✅ Receipt Found:", row)

    # Convert values
    monthly_fee = float(row.get('monthly_fee') or 0.0)
    total_paid = float(row.get('total_paid') or 0.0)
    item_price_total = float(row.get('item_price_total') or 0.0)
    service_fee = round(item_price_total - monthly_fee, 2)

    booking_paid_date = row.get('booking_paid_date')
    if isinstance(booking_paid_date, datetime):
        booking_paid_date = booking_paid_date.strftime('%Y-%m-%d %H:%M:%S')
    elif booking_paid_date is None:
        booking_paid_date = ''

    return ReceiptModel(
        booking_id=str(booking_id),
        inv_no=str(invno),
        property_title=row.get('post_title', ''),
        property_address=row.get('property_address', ''),
        guest_full_name=f"{row.get('first_name', '')} {row.get('last_name', '')}".strip(),
        email=email,
        monthly_fee=monthly_fee,
        total_paid=total_paid,
        service_fee=service_fee,
        invoice_date=row.get('invoice_date', ''),
        booking_paid_date=booking_paid_date
    )
