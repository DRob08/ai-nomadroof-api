import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_data_from_db():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

        cursor = connection.cursor(dictionary=True)  # Return rows as dicts for easy reading
        query = """
            SELECT ID, post_title, post_date, post_status, post_type
            FROM wp_posts
            WHERE post_status = 'publish' AND post_type = 'post'
            ORDER BY post_date DESC
            LIMIT 5;
        """
        cursor.execute(query)
        results = cursor.fetchall()

        return results

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_booking_data():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT wp_posts.post_date, wp_posts.post_title, m2.meta_key, m2.meta_value as check_in, 
               m1.meta_key, m1.meta_value as booking_status, u1.id, u1.user_login, wp_posts.ID, um.meta_value as first_name, 
               u1.user_email, m3.meta_value, uown.user_email as owner_email, m4.meta_value as check_out, 
               m5.meta_value as prop_id, uown.user_nicename as owneralias, b.post_title as prop_name
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
        WHERE wp_posts.post_type = 'wpestate_booking'
        AND wp_posts.post_status = 'publish'
        AND ( m1.meta_key = 'booking_status' AND m1.meta_value IN ('pending', 'waiting', 'confirmed', 'canceled') )

        AND ( m2.meta_key = 'booking_from_date' )
        AND ( m3.meta_key = 'owner_id' AND m3.meta_value <> u1.id )
        AND ( um.meta_key = 'first_name' AND LENGTH(um.meta_value) > 0 )
        AND ( m4.meta_key = 'booking_to_date' )
        AND ( m5.meta_key = 'booking_id' )
        AND STR_TO_DATE(wp_posts.post_date,'%Y-%m-%d') >= '2022-01-01'
        ORDER BY wp_posts.post_date DESC;
        """

        cursor.execute(query)
        results = cursor.fetchall()
        print(results)
        return results

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

