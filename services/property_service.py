from models.property_model import PropertyModel
from typing import List
from services.db_service import fetch_all

#def get_available_properties(filters: dict) -> List[PropertyModel]:
def get_available_properties(filters: dict = {}) -> List[PropertyModel]:
    print(filters)
    query = """
          SELECT 
                p.post_title,
                past_bookings.prop_id AS past_bookings_ptroperty_id,
                p.post_name AS half_property_url,
                thumbnail.meta_value AS thumbnail_id,
                CONCAT('https://www.nomadroof.com/wp-content/uploads/', thumbnail_file.meta_value) AS full_thumbnail_url,
                size.meta_value AS property_size,
                rooms.meta_value AS property_rooms,
                bedrooms.meta_value AS property_bedrooms,
                bathrooms.meta_value AS property_bathrooms,
                address.meta_value AS property_address,
                state.meta_value AS property_state,
                county.meta_value AS property_county,
              CASE WHEN electricity.meta_value = '1' THEN TRUE ELSE FALSE END AS electricity_included,
                CASE WHEN pool.meta_value = '1' THEN TRUE ELSE FALSE END AS pool,
                CASE WHEN water.meta_value = '1' THEN TRUE ELSE FALSE END AS water_included,
                CASE WHEN gym.meta_value = '1' THEN TRUE ELSE FALSE END AS gym,
                CASE WHEN heating.meta_value = '1' THEN TRUE ELSE FALSE END AS heating,
                CASE WHEN hot_tub.meta_value = '1' THEN TRUE ELSE FALSE END AS hot_tub,
                CASE WHEN air_conditioning.meta_value = '1' THEN TRUE ELSE FALSE END AS air_conditioning,
                CASE WHEN parking.meta_value = '1' THEN TRUE ELSE FALSE END AS free_parking_on_premises,
                CASE WHEN desk.meta_value = '1' THEN TRUE ELSE FALSE END AS desk,
                CASE WHEN hangers.meta_value = '1' THEN TRUE ELSE FALSE END AS hangers,
                CASE WHEN closet.meta_value = '1' THEN TRUE ELSE FALSE END AS closet,
                CASE WHEN iron.meta_value = '1' THEN TRUE ELSE FALSE END AS iron,
                                country.meta_value AS property_country,
                guest.meta_value AS guest_no,
                price.meta_value AS property_price,
                price_per_month.meta_value AS property_price_per_month,
                uni.meta_value AS uni_nearby,
                CASE
                    WHEN LOCATE('SPANISH', neighborhood.meta_value) > 0 THEN 
                        SUBSTRING(neighborhood.meta_value, 1, LOCATE('SPANISH', neighborhood.meta_value) - 1)
                    ELSE 
                        neighborhood.meta_value
                END AS about_neighborhood,
                cancel_policy.meta_value AS cancellation_policy,
                admin_area.meta_value AS property_admin_area,
                u1.display_name AS owner_name,
                um.meta_value AS owner_first_name,

                CASE
                    WHEN LOCATE('SPANISH', bedroom_descr.meta_value) > 0 THEN 
                        SUBSTRING(bedroom_descr.meta_value, 1, LOCATE('SPANISH', bedroom_descr.meta_value) - 1)
                    ELSE 
                        bedroom_descr.meta_value
                    END AS bedroom_descr
            FROM 
                wp_posts p
            INNER JOIN 
                wp_postmeta thumbnail ON p.ID = thumbnail.post_id AND thumbnail.meta_key = '_thumbnail_id'
            INNER JOIN 
                wp_postmeta bedroom_descr ON p.ID = bedroom_descr.post_id AND bedroom_descr.meta_key = 'bedroom_descr'
            INNER JOIN 
                wp_postmeta thumbnail_file ON thumbnail.meta_value = thumbnail_file.post_id AND thumbnail_file.meta_key = '_wp_attached_file'
            INNER JOIN 
                wp_postmeta size ON p.ID = size.post_id AND size.meta_key = 'property_size'
            INNER JOIN 
                wp_postmeta rooms ON p.ID = rooms.post_id AND rooms.meta_key = 'property_rooms'
            INNER JOIN 
                wp_postmeta bedrooms ON p.ID = bedrooms.post_id AND bedrooms.meta_key = 'property_bedrooms'
            INNER JOIN 
                wp_postmeta bathrooms ON p.ID = bathrooms.post_id AND bathrooms.meta_key = 'property_bathrooms'
            INNER JOIN 
                wp_postmeta cancellation ON p.ID = cancellation.post_id AND cancellation.meta_key = 'cancellation'
            INNER JOIN 
                wp_postmeta address ON p.ID = address.post_id AND address.meta_key = 'property_address'
            INNER JOIN 
                wp_postmeta state ON p.ID = state.post_id AND state.meta_key = 'property_state'
            INNER JOIN 
                wp_postmeta county ON p.ID = county.post_id AND county.meta_key = 'property_county'
            LEFT JOIN
                wp_postmeta electricity ON p.ID = electricity.post_id AND electricity.meta_key = 'electricity_included'
            LEFT JOIN
                wp_postmeta pool ON p.ID = pool.post_id AND pool.meta_key = 'pool'
            LEFT JOIN
                wp_postmeta water ON p.ID = water.post_id AND water.meta_key = 'water_included'
            LEFT JOIN
                wp_postmeta gym ON p.ID = gym.post_id AND gym.meta_key = 'gym'
            LEFT JOIN 
                wp_postmeta heating ON p.ID = heating.post_id AND heating.meta_key = 'heating'
            LEFT JOIN
                wp_postmeta hot_tub ON p.ID = hot_tub.post_id AND hot_tub.meta_key = 'hot_tub'
            LEFT JOIN 
                wp_postmeta air_conditioning ON p.ID = air_conditioning.post_id AND air_conditioning.meta_key = 'air_conditioning'
            LEFT JOIN
                wp_postmeta parking ON p.ID = parking.post_id AND parking.meta_key = 'free_parking_on_premises'
            LEFT JOIN
                wp_postmeta desk ON p.ID = desk.post_id AND desk.meta_key = 'desk'
            LEFT JOIN 
                wp_postmeta hangers ON p.ID = hangers.post_id AND hangers.meta_key = 'hangers'
            LEFT JOIN
                wp_postmeta closet ON p.ID = closet.post_id AND closet.meta_key = 'closet'
            LEFT JOIN
                wp_postmeta iron ON p.ID = iron.post_id AND iron.meta_key = 'iron'
            INNER JOIN 
                wp_postmeta country ON p.ID = country.post_id AND country.meta_key = 'property_country'
            INNER JOIN 
                wp_postmeta guest ON p.ID = guest.post_id AND guest.meta_key = 'guest_no'
            INNER JOIN 
                wp_postmeta price ON p.ID = price.post_id AND price.meta_key = 'property_price'
            INNER JOIN 
                wp_postmeta price_per_month ON p.ID = price_per_month.post_id AND price_per_month.meta_key = 'property_price_per_month'
            INNER JOIN 
                wp_postmeta uni ON p.ID = uni.post_id AND uni.meta_key = 'uni_nearby'
            INNER JOIN 
                wp_postmeta neighborhood ON p.ID = neighborhood.post_id AND neighborhood.meta_key = 'about_neighborhood'
            INNER JOIN 
                wp_postmeta cancel_policy ON p.ID = cancel_policy.post_id AND cancel_policy.meta_key = 'cancellation_policy'
            INNER JOIN 
                wp_postmeta admin_area ON p.ID = admin_area.post_id AND admin_area.meta_key = 'property_admin_area'
            LEFT JOIN 
                wp_postmeta global_prop ON p.ID = global_prop.post_id AND global_prop.meta_key = 'global_prop'
            LEFT JOIN (
                SELECT DISTINCT m5.meta_value AS prop_id
                FROM wp_posts
                INNER JOIN wp_postmeta m1 ON wp_posts.ID = m1.post_id
                INNER JOIN wp_postmeta m2 ON wp_posts.ID = m2.post_id
                INNER JOIN wp_postmeta m3 ON wp_posts.ID = m3.post_id
                INNER JOIN wp_postmeta m4 ON wp_posts.ID = m4.post_id
                INNER JOIN wp_users u1 ON wp_posts.post_author = u1.ID
                INNER JOIN wp_usermeta um ON u1.ID = um.user_id
                INNER JOIN wp_users uown ON m3.meta_value = uown.id
                INNER JOIN wp_postmeta m5 ON wp_posts.ID = m5.post_id
                INNER JOIN wp_posts b ON m5.meta_value = b.ID
                INNER JOIN wp_postmeta m6 ON wp_posts.ID = m6.post_id
                WHERE wp_posts.post_type = 'wpestate_booking'
                AND wp_posts.post_status = 'publish'
                AND m1.meta_key = 'booking_status'
                AND m1.meta_value = 'confirmed'
                AND m2.meta_key = 'booking_from_date'
AND STR_TO_DATE(m2.meta_value, '%M %d, %Y') >= DATE_SUB(CURRENT_DATE, INTERVAL 1 YEAR)
AND STR_TO_DATE(m2.meta_value, '%M %d, %Y') < CURRENT_DATE

                AND m3.meta_key = 'owner_id' AND m3.meta_value <> u1.id
                AND (um.meta_key = 'first_name' AND LENGTH(um.meta_value) > 0)
                AND m4.meta_key = 'booking_to_date'
                AND m5.meta_key = 'booking_id'
                AND m6.meta_key = 'booking_invoice_no'
            ) AS past_bookings ON p.ID = past_bookings.prop_id
            INNER JOIN wp_users u1 ON p.post_author = u1.ID
            INNER JOIN wp_usermeta um ON u1.ID = um.user_id AND um.meta_key = 'first_name'
            WHERE 
                p.post_type = 'estate_property' 
                AND p.post_status = 'publish' 
                AND global_prop.meta_value = 'NO'
                AND p.ID NOT IN (
                   SELECT DISTINCT m5.meta_value AS prop_id
                    FROM wp_posts
                    INNER JOIN wp_postmeta m1 ON wp_posts.ID = m1.post_id -- booking_status
                    INNER JOIN wp_postmeta m2 ON wp_posts.ID = m2.post_id -- booking_from_date
                    INNER JOIN wp_postmeta m3 ON wp_posts.ID = m3.post_id -- owner_id
                    INNER JOIN wp_postmeta m4 ON wp_posts.ID = m4.post_id -- booking_to_date
                    INNER JOIN wp_users u1 ON wp_posts.post_author = u1.ID
                    INNER JOIN wp_usermeta um ON u1.ID = um.user_id
                    INNER JOIN wp_users uown ON m3.meta_value = uown.id
                    INNER JOIN wp_postmeta m5 ON wp_posts.ID = m5.post_id -- booking_id (prop_id)
                    INNER JOIN wp_posts b ON m5.meta_value = b.ID -- actual property post
                    INNER JOIN wp_postmeta m6 ON wp_posts.ID = m6.post_id -- booking_invoice_no
                    WHERE wp_posts.post_type = 'wpestate_booking'
                      AND wp_posts.post_status = 'publish'
                      AND m1.meta_key = 'booking_status' AND m1.meta_value = 'confirmed'
                      AND m2.meta_key = 'booking_from_date'
                      AND m4.meta_key = 'booking_to_date'
                      AND (
                        -- Overlaps with today or is in the next year
                        STR_TO_DATE(m4.meta_value, '%M %d, %Y') >= CURDATE() -- ends today or later
                        AND STR_TO_DATE(m2.meta_value, '%M %d, %Y') <= CURDATE() + INTERVAL 1 YEAR -- starts within a year
                      )
                      AND m3.meta_key = 'owner_id' AND m3.meta_value <> u1.id
                      AND (um.meta_key = 'first_name' AND LENGTH(um.meta_value) > 0)
                      AND m5.meta_key = 'booking_id'
                      AND m6.meta_key = 'booking_invoice_no'
                )
                AND country.meta_value = 'Peru'
                AND past_bookings.prop_id IS NOT NULL
            ORDER BY p.post_title ASC;
            """ # The giant query you pasted
    results = fetch_all(query)
    return [PropertyModel(**row) for row in results]