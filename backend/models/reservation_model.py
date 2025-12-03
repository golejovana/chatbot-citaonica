from db import get_db_connection
from datetime import datetime

def reserve_seat(user_id: int, seat_number: int, date):
    """
    Rezerviše mesto po datumu.
    """

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # 1. Da li mesto postoji
    cursor.execute("SELECT id FROM seats WHERE seat_number = %s", (seat_number,))
    seat = cursor.fetchone()
    if not seat:
        return False, "To mesto ne postoji."

    # 2. Da li je već rezervisano za taj dan
    cursor.execute("""
        SELECT id FROM reservations
        WHERE seat_number = %s AND date = %s AND status = 'active'
    """, (seat_number, date))
    taken = cursor.fetchone()

    if taken:
        return False, "To mesto je već rezervisano za taj datum."

    # 3. Da li korisnik već ima rezervaciju za taj dan
    cursor.execute("""
        SELECT id FROM reservations
        WHERE user_id = %s AND date = %s AND status = 'active'
    """, (user_id, date))
    existing = cursor.fetchone()

    if existing:
        return False, "Već imaš rezervisano mesto za taj dan."

    # 4. Upis rezervacije
    cursor.execute("""
        INSERT INTO reservations (user_id, seat_number, date, status)
        VALUES (%s, %s, %s, 'active')
    """, (user_id, seat_number, date))

    db.commit()
    db.close()

    return True, f"Uspešno si rezervisao mesto {seat_number} za datum {date} 😊"


def cancel_reservation(user_id, seat_number, date):
    """
    Otkazuje rezervaciju (menja status).
    """

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT id FROM reservations
        WHERE user_id = %s AND seat_number = %s AND date = %s AND status = 'active'
    """, (user_id, seat_number, date))
    
    reservation = cursor.fetchone()

    if not reservation:
        return False, "Nemaš aktivnu rezervaciju za zadati datum."

    cursor.execute("""
        UPDATE reservations
        SET status = 'cancelled'
        WHERE id = %s
    """, (reservation["id"],))

    db.commit()
    db.close()

    return True, f"Rezervacija mesta {seat_number} za datum {date} je otkazana."
