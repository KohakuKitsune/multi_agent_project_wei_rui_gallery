import psycopg2
from config.settings import DB_CONFIG

def save_order_to_db(order_data):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO orders (customer_name, frame_size, wood_type, finish, image_url)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            order_data['customer_name'],
            order_data['frame_size'],
            order_data['wood_type'],
            order_data['finish'],
            order_data['image_url']
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return "Order saved successfully."
    except Exception as e:
        return f"Failed to save order: {str(e)}"