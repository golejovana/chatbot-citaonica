from db import get_db_connection

def get_free_seats(date):
    """
    Vraća sva slobodna mesta za dati datum.
    """
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT seat_number 
        FROM seats
        WHERE seat_number NOT IN (
            SELECT seat_number FROM reservations
            WHERE date = %s AND status = 'active'
        )
        ORDER BY seat_number ASC
    """, (date,))

    result = cursor.fetchall()
    db.close()

    return [row["seat_number"] for row in result]
