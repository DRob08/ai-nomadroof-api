from models.property_model import PropertyModel
from typing import List
from services.db_service import fetch_all
import phpserialize
from datetime import datetime
import os

def parse_property_available_days(avail_days_raw):
    try:
        if isinstance(avail_days_raw, str):
            # Remove leading `s:N:` wrapper if it exists
            if avail_days_raw.startswith("s:"):
                first_quote = avail_days_raw.find('"')
                last_quote = avail_days_raw.rfind('"')
                avail_days_raw = avail_days_raw[first_quote + 1:last_quote]

            data = phpserialize.loads(avail_days_raw.encode(), decode_strings=True)
            return data
        return {}
    except Exception as e:
        print(f"Error deserializing PHP data: {e}")
        return {}

def is_property_available(property_data, start_date, end_date):
    print("Checking property availability...")
    print(f"Received start_date: {start_date}, end_date: {end_date}")

    avail_days_raw = property_data.get("property_available_days")
    prop_name = property_data.get("post_title")
    print(prop_name)
    #print(f"Raw availability data: {avail_days_raw}")
    if not avail_days_raw:
        print("No availability data found.")
        return False

    data = parse_property_available_days(avail_days_raw)
    print(f"Parsed availability data: {data} (type: {type(data)})")

    if not isinstance(data, dict):
        print("Error: Parsed data is not a dictionary.")
        return False

    if data.get("unlimited") == "yes":
        print("Unlimited availability detected.")
        start_str = data.get("start")
        #print(f"Start limit string from data: {start_str}")
        if not start_str:
            print("Start limit is missing.")
            return False
        try:
           # start_limit = datetime.strptime(start_str, "%Y-%m-%d")  # Assuming this format
            start_limit = datetime.strptime(start_str, "%b %d, %Y")

            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            print(f"Parsed dates - start_limit: {start_limit}, start_dt: {start_dt}, end_dt: {end_dt}")
        except ValueError as e:
            print(f"Date parsing error: {e}")
            return False

        #result = start_dt >= start_limit and end_dt >= start_limit
        result = start_dt <= start_limit <= end_dt

        gap_days = (start_limit - start_dt).days
        result = 0 <= gap_days <= 7

        print(f"Availability result: {result}")
        return result

    print("Availability is not unlimited.")
    return False


def get_available_properties(filters: dict = {}) -> List[PropertyModel]:
    print(filters)

    start_date = filters.get("startDate")
    end_date = filters.get("endDate")
    min_price = filters.get("minPrice")
    max_price = filters.get("maxPrice")
    latitude = filters.get("districtLat")
    longitude = filters.get("districtLng")

    date_conditions = ""
    price_conditions = ""

    location_condition = ""
    if latitude and longitude:
        location_condition = f"""
            AND (
                6371 * acos(
                    cos(radians({latitude}))
                    * cos(radians(CAST(property_latitude.meta_value AS DECIMAL(10, 6))))
                    * cos(radians(CAST(property_longitude.meta_value AS DECIMAL(10, 6))) - radians({longitude}))
                    + sin(radians({latitude}))
                    * sin(radians(CAST(property_latitude.meta_value AS DECIMAL(10, 6))))
                )
            ) <= 10
        """
    
    if start_date and end_date:
        date_conditions = f"""
           AND NOT EXISTS (
    SELECT 1
    FROM wp_posts booking_post
    -- Booking status
    INNER JOIN wp_postmeta booking_status_meta 
        ON booking_post.ID = booking_status_meta.post_id AND booking_status_meta.meta_key = 'booking_status'
    -- Booking start date
    INNER JOIN wp_postmeta booking_start_meta 
        ON booking_post.ID = booking_start_meta.post_id AND booking_start_meta.meta_key = 'booking_from_date'
    -- Booking end date
    INNER JOIN wp_postmeta booking_end_meta 
        ON booking_post.ID = booking_end_meta.post_id AND booking_end_meta.meta_key = 'booking_to_date'
    -- Owner ID of the property
    INNER JOIN wp_postmeta owner_id_meta 
        ON booking_post.ID = owner_id_meta.post_id AND owner_id_meta.meta_key = 'owner_id'
    -- The user who booked (booker)
    INNER JOIN wp_users user_booker 
        ON booking_post.post_author = user_booker.ID
    -- Booker's first name
    INNER JOIN wp_usermeta user_booker_firstname 
        ON user_booker.ID = user_booker_firstname.user_id 
        AND user_booker_firstname.meta_key = 'first_name' AND LENGTH(user_booker_firstname.meta_value) > 0
    -- Property owner (joined via owner_id_meta)
    INNER JOIN wp_users user_owner 
        ON owner_id_meta.meta_value = user_owner.ID 
    -- Booking meta linking to property (via booking_id)
    INNER JOIN wp_postmeta booking_property_meta 
        ON booking_post.ID = booking_property_meta.post_id AND booking_property_meta.meta_key = 'booking_id'
    -- Actual property post
    INNER JOIN wp_posts property_post 
        ON booking_property_meta.meta_value = property_post.ID
    -- Booking invoice number (exists, but not used directly in condition)
    INNER JOIN wp_postmeta invoice_number_meta 
        ON booking_post.ID = invoice_number_meta.post_id AND invoice_number_meta.meta_key = 'booking_invoice_no'
    WHERE 
        booking_post.post_type = 'wpestate_booking'
        AND booking_post.post_status = 'publish'
        AND booking_status_meta.meta_value = 'confirmed'
        
        AND booking_property_meta.meta_value = p.ID
      AND (
    STR_TO_DATE(booking_start_meta.meta_value, '%b %d, %Y') <= '{end_date}'
    AND STR_TO_DATE(booking_end_meta.meta_value, '%b %d, %Y') >= '{start_date}'
)


)

        """
    else:
        date_conditions = ""

     # Handling price range condition
    if min_price is not None or max_price is not None:
        price_conditions = "AND price_per_month.meta_value BETWEEN "
        
        if min_price is not None and max_price is not None:
            price_conditions += f"'{min_price}' AND '{max_price}'"
        elif min_price is not None:
            price_conditions += f"'{min_price}' AND '{max_price}'"  # Handle only max price scenario
        elif max_price is not None:
            price_conditions += f"'{max_price}'"  # Handle only min price scenario

    # district = filters.get("district")
    
    # district_condition = ""
    # if district:
    #     district_condition = f"AND address.meta_value LIKE '%{district}%'"
    district = filters.get("district")
    district_join = ""
    district_condition = ""

    district_select=""

    if district:
        district_join = f"""
                        LEFT JOIN wp_term_relationships wtr ON p.ID = wtr.object_id
                        LEFT JOIN wp_term_taxonomy wtt ON wtt.term_taxonomy_id = wtr.term_taxonomy_id
                        LEFT JOIN wp_terms wt ON wt.term_id = wtt.term_id
                    
                        """
        district_select=f"""
        wt.name as property_district,    
        """


    district_condition = f"""
            AND (
                (wt.name IS NOT NULL AND wt.name LIKE '%%{district}%%')
                OR (wt.name IS NULL AND address.meta_value LIKE '%%{district}%%')
            )
        """



    query = f"""
        SELECT 
        p.post_title,
        p.ID as property_id,
        {district_select}
        NULL AS past_bookings_property_id,
        p.post_name AS half_property_url,
        thumbnail.meta_value AS thumbnail_id,
        CONCAT('https://www.nomadroof.com/wp-content/uploads/', thumbnail_file.meta_value) AS full_thumbnail_url,
        size.meta_value AS property_size,
        rooms.meta_value AS property_rooms,
        bedrooms.meta_value AS property_bedrooms,
        bathrooms.meta_value AS property_bathrooms,
        address.meta_value AS property_address,
        state.meta_value AS property_state,
        county.meta_value AS property_country,
        property_latitude.meta_value AS property_latitude,
        property_longitude.meta_value AS property_longitude,
        property_available_days.meta_value AS property_available_days,
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
    
        CASE WHEN prop_featured.meta_value = '1' THEN TRUE ELSE FALSE END AS is_prop_featured,
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
        booking_dates.meta_value AS property_booking_dates,
        CASE
            WHEN LOCATE('SPANISH', bedroom_descr.meta_value) > 0 THEN 
                SUBSTRING(bedroom_descr.meta_value, 1, LOCATE('SPANISH', bedroom_descr.meta_value) - 1)
            ELSE 
                bedroom_descr.meta_value
            END AS bedroom_descr
    FROM 
        wp_posts p
    LEFT JOIN wp_postmeta thumbnail ON p.ID = thumbnail.post_id AND thumbnail.meta_key = '_thumbnail_id'
    LEFT JOIN wp_postmeta bedroom_descr ON p.ID = bedroom_descr.post_id AND bedroom_descr.meta_key = 'bedroom_descr'
    LEFT JOIN wp_postmeta thumbnail_file ON thumbnail.meta_value = thumbnail_file.post_id AND thumbnail_file.meta_key = '_wp_attached_file'
    INNER JOIN wp_postmeta size ON p.ID = size.post_id AND size.meta_key = 'property_size'
    INNER JOIN wp_postmeta rooms ON p.ID = rooms.post_id AND rooms.meta_key = 'property_rooms'
    INNER JOIN wp_postmeta bedrooms ON p.ID = bedrooms.post_id AND bedrooms.meta_key = 'property_bedrooms'
    INNER JOIN wp_postmeta bathrooms ON p.ID = bathrooms.post_id AND bathrooms.meta_key = 'property_bathrooms'
    INNER JOIN wp_postmeta cancellation ON p.ID = cancellation.post_id AND cancellation.meta_key = 'cancellation'
    INNER JOIN wp_postmeta address ON p.ID = address.post_id AND address.meta_key = 'property_address'
    INNER JOIN wp_postmeta state ON p.ID = state.post_id AND state.meta_key = 'property_state'
    INNER JOIN wp_postmeta county ON p.ID = county.post_id AND county.meta_key = 'property_country'
    LEFT JOIN wp_postmeta electricity ON p.ID = electricity.post_id AND electricity.meta_key = 'electricity_included'
    LEFT JOIN wp_postmeta pool ON p.ID = pool.post_id AND pool.meta_key = 'pool'
    LEFT JOIN wp_postmeta water ON p.ID = water.post_id AND water.meta_key = 'water_included'
    LEFT JOIN wp_postmeta gym ON p.ID = gym.post_id AND gym.meta_key = 'gym'
    LEFT JOIN wp_postmeta heating ON p.ID = heating.post_id AND heating.meta_key = 'heating'
    LEFT JOIN wp_postmeta hot_tub ON p.ID = hot_tub.post_id AND hot_tub.meta_key = 'hot_tub'
    LEFT JOIN wp_postmeta air_conditioning ON p.ID = air_conditioning.post_id AND air_conditioning.meta_key = 'air_conditioning'
    LEFT JOIN wp_postmeta parking ON p.ID = parking.post_id AND parking.meta_key = 'free_parking_on_premises'
    LEFT JOIN wp_postmeta desk ON p.ID = desk.post_id AND desk.meta_key = 'desk'
    LEFT JOIN wp_postmeta hangers ON p.ID = hangers.post_id AND hangers.meta_key = 'hangers'
    LEFT JOIN wp_postmeta closet ON p.ID = closet.post_id AND closet.meta_key = 'closet'
    LEFT JOIN wp_postmeta iron ON p.ID = iron.post_id AND iron.meta_key = 'iron'
    INNER JOIN wp_postmeta country ON p.ID = country.post_id AND country.meta_key = 'property_country'
    INNER JOIN wp_postmeta guest ON p.ID = guest.post_id AND guest.meta_key = 'guest_no'
    INNER JOIN wp_postmeta price ON p.ID = price.post_id AND price.meta_key = 'property_price'
    INNER JOIN wp_postmeta price_per_month ON p.ID = price_per_month.post_id AND price_per_month.meta_key = 'property_price_per_month'
    LEFT JOIN wp_postmeta uni ON p.ID = uni.post_id AND uni.meta_key = 'uni_nearby'
    LEFT JOIN wp_postmeta neighborhood ON p.ID = neighborhood.post_id AND neighborhood.meta_key = 'about_neighborhood'
    INNER JOIN wp_postmeta cancel_policy ON p.ID = cancel_policy.post_id AND cancel_policy.meta_key = 'cancellation_policy'
    INNER JOIN wp_postmeta admin_area ON p.ID = admin_area.post_id AND admin_area.meta_key = 'property_admin_area'
    LEFT JOIN wp_postmeta global_prop ON p.ID = global_prop.post_id AND global_prop.meta_key = 'global_prop'
    LEFT JOIN wp_postmeta booking_dates ON p.ID = booking_dates.post_id AND booking_dates.meta_key = 'booking_dates'
    INNER JOIN wp_users u1 ON p.post_author = u1.ID
    INNER JOIN wp_usermeta um ON u1.ID = um.user_id AND um.meta_key = 'first_name'
    {district_join}
    LEFT JOIN wp_postmeta property_latitude ON p.ID = property_latitude.post_id AND property_latitude.meta_key = 'property_latitude'
    LEFT JOIN wp_postmeta property_longitude ON p.ID = property_longitude.post_id AND property_longitude.meta_key = 'property_longitude'
    LEFT JOIN wp_postmeta property_available_days ON p.ID = property_available_days.post_id AND property_available_days.meta_key = 'property_available_days'
    LEFT JOIN wp_postmeta prop_featured ON p.ID = prop_featured.post_id AND prop_featured.meta_key = 'prop_featured' 
    
    WHERE 
        p.post_type = 'estate_property' 
        AND p.post_status = 'publish' 
        AND global_prop.meta_value = 'NO'
        AND country.meta_value = 'Peru'
        {date_conditions}
        {price_conditions}
        {location_condition}
        {district_condition}
   
    ORDER BY 
    CAST(prop_featured.meta_value AS UNSIGNED) DESC,
    p.post_title ASC;
    """
    
    # Print the final query for debugging purposes
    #print(query)

    # Fetch all results from the database
    results = fetch_all(query)

    print(results)

    filtered_results = [
        prop for prop in results
        if is_property_available(prop, start_date, end_date)
    ]

    #print(filtered_results)
    
    # Return the results as a list of PropertyModel objects
    return [PropertyModel(**row) for row in filtered_results]
    #return [PropertyModel(**row) for row in results]



def get_exclusive_properties() -> List[PropertyModel]:
    # Read property IDs from .env
    ids_string = os.getenv("EXCLUSIVE_PROPERTY_IDS", "")
    if not ids_string:
        print("No EXCLUSIVE_PROPERTY_IDS found in .env")
        return []

    # Sanitize and format for SQL
    try:
        ids_list = [int(pid.strip()) for pid in ids_string.split(",") if pid.strip().isdigit()]
        if not ids_list:
            print("No valid property IDs found.")
            return []
    except Exception as e:
        print(f"Error parsing property IDs: {e}")
        return []

    ids_sql = ", ".join(map(str, ids_list))

    query = f"""
         SELECT 
        p.post_title,
        p.ID as property_id,
        NULL AS past_bookings_property_id,
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
        property_latitude.meta_value AS property_latitude,
        property_longitude.meta_value AS property_longitude,
        property_available_days.meta_value AS property_available_days,
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
    
        CASE WHEN prop_featured.meta_value = '1' THEN TRUE ELSE FALSE END AS is_prop_featured,
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
        booking_dates.meta_value AS property_booking_dates,
        CASE
            WHEN LOCATE('SPANISH', bedroom_descr.meta_value) > 0 THEN 
                SUBSTRING(bedroom_descr.meta_value, 1, LOCATE('SPANISH', bedroom_descr.meta_value) - 1)
            ELSE 
                bedroom_descr.meta_value
            END AS bedroom_descr
    FROM 
        wp_posts p
    INNER JOIN wp_postmeta thumbnail ON p.ID = thumbnail.post_id AND thumbnail.meta_key = '_thumbnail_id'
    INNER JOIN wp_postmeta bedroom_descr ON p.ID = bedroom_descr.post_id AND bedroom_descr.meta_key = 'bedroom_descr'
    INNER JOIN wp_postmeta thumbnail_file ON thumbnail.meta_value = thumbnail_file.post_id AND thumbnail_file.meta_key = '_wp_attached_file'
    INNER JOIN wp_postmeta size ON p.ID = size.post_id AND size.meta_key = 'property_size'
    INNER JOIN wp_postmeta rooms ON p.ID = rooms.post_id AND rooms.meta_key = 'property_rooms'
    INNER JOIN wp_postmeta bedrooms ON p.ID = bedrooms.post_id AND bedrooms.meta_key = 'property_bedrooms'
    INNER JOIN wp_postmeta bathrooms ON p.ID = bathrooms.post_id AND bathrooms.meta_key = 'property_bathrooms'
    INNER JOIN wp_postmeta cancellation ON p.ID = cancellation.post_id AND cancellation.meta_key = 'cancellation'
    INNER JOIN wp_postmeta address ON p.ID = address.post_id AND address.meta_key = 'property_address'
    INNER JOIN wp_postmeta state ON p.ID = state.post_id AND state.meta_key = 'property_state'
    INNER JOIN wp_postmeta county ON p.ID = county.post_id AND county.meta_key = 'property_county'
    LEFT JOIN wp_postmeta electricity ON p.ID = electricity.post_id AND electricity.meta_key = 'electricity_included'
    LEFT JOIN wp_postmeta pool ON p.ID = pool.post_id AND pool.meta_key = 'pool'
    LEFT JOIN wp_postmeta water ON p.ID = water.post_id AND water.meta_key = 'water_included'
    LEFT JOIN wp_postmeta gym ON p.ID = gym.post_id AND gym.meta_key = 'gym'
    LEFT JOIN wp_postmeta heating ON p.ID = heating.post_id AND heating.meta_key = 'heating'
    LEFT JOIN wp_postmeta hot_tub ON p.ID = hot_tub.post_id AND hot_tub.meta_key = 'hot_tub'
    LEFT JOIN wp_postmeta air_conditioning ON p.ID = air_conditioning.post_id AND air_conditioning.meta_key = 'air_conditioning'
    LEFT JOIN wp_postmeta parking ON p.ID = parking.post_id AND parking.meta_key = 'free_parking_on_premises'
    LEFT JOIN wp_postmeta desk ON p.ID = desk.post_id AND desk.meta_key = 'desk'
    LEFT JOIN wp_postmeta hangers ON p.ID = hangers.post_id AND hangers.meta_key = 'hangers'
    LEFT JOIN wp_postmeta closet ON p.ID = closet.post_id AND closet.meta_key = 'closet'
    LEFT JOIN wp_postmeta iron ON p.ID = iron.post_id AND iron.meta_key = 'iron'
    INNER JOIN wp_postmeta country ON p.ID = country.post_id AND country.meta_key = 'property_country'
    INNER JOIN wp_postmeta guest ON p.ID = guest.post_id AND guest.meta_key = 'guest_no'
    INNER JOIN wp_postmeta price ON p.ID = price.post_id AND price.meta_key = 'property_price'
    INNER JOIN wp_postmeta price_per_month ON p.ID = price_per_month.post_id AND price_per_month.meta_key = 'property_price_per_month'
    INNER JOIN wp_postmeta uni ON p.ID = uni.post_id AND uni.meta_key = 'uni_nearby'
    INNER JOIN wp_postmeta neighborhood ON p.ID = neighborhood.post_id AND neighborhood.meta_key = 'about_neighborhood'
    INNER JOIN wp_postmeta cancel_policy ON p.ID = cancel_policy.post_id AND cancel_policy.meta_key = 'cancellation_policy'
    INNER JOIN wp_postmeta admin_area ON p.ID = admin_area.post_id AND admin_area.meta_key = 'property_admin_area'
    LEFT JOIN wp_postmeta global_prop ON p.ID = global_prop.post_id AND global_prop.meta_key = 'global_prop'
    LEFT JOIN wp_postmeta booking_dates ON p.ID = booking_dates.post_id AND booking_dates.meta_key = 'booking_dates'
    INNER JOIN wp_users u1 ON p.post_author = u1.ID
    INNER JOIN wp_usermeta um ON u1.ID = um.user_id AND um.meta_key = 'first_name'
    LEFT JOIN wp_postmeta property_latitude ON p.ID = property_latitude.post_id AND property_latitude.meta_key = 'property_latitude'
    LEFT JOIN wp_postmeta property_longitude ON p.ID = property_longitude.post_id AND property_longitude.meta_key = 'property_longitude'
    LEFT JOIN wp_postmeta property_available_days ON p.ID = property_available_days.post_id AND property_available_days.meta_key = 'property_available_days'
    LEFT JOIN wp_postmeta prop_featured ON p.ID = prop_featured.post_id AND prop_featured.meta_key = 'prop_featured' 

    WHERE  
            p.post_type = 'estate_property' 
            AND p.post_status = 'publish'
            AND p.ID IN ({ids_sql})
    """

    result = fetch_all(query)

    return [PropertyModel(**row) for row in result]
