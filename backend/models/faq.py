import re
from datetime import datetime, timedelta
from flask import session

from models.seats import get_free_seats
from models.reservation_model import reserve_seat, cancel_reservation
from models.faq_data import FAQ_DATA


# ============================================================
#   HELPER FUNKCIJE
# ============================================================

def normalize(text: str) -> str:
    msg = text.lower()
    msg = re.sub(r"[^\wšđčćž ]+", " ", msg)
    return msg.strip()


def parse_date(text: str):
    """Prepoznaje danas / sutra / za X dana + standardne formate datuma."""
    raw = text.strip().lower()

    # danas / sutra / prekosutra
    if raw == "danas":
        return datetime.now().date()
    if raw == "sutra":
        return datetime.now().date() + timedelta(days=1)
    if raw == "prekosutra":
        return datetime.now().date() + timedelta(days=2)

    # za X dana
    m = re.search(r"za\s+(\d+)\s+dana", raw)
    if m:
        return datetime.now().date() + timedelta(days=int(m.group(1)))

    # dd.mm.yyyy / dd-mm-yyyy / dd/mm/yyyy
    m = re.search(r"(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{4})", raw)
    if m:
        d, m_, y = m.groups()
        return datetime(int(y), int(m_), int(d)).date()

    # yyyy-mm-dd
    m = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", raw)
    if m:
        y, m_, d = m.groups()
        return datetime(int(y), int(m_), int(d)).date()

    return None


# ============================================================
#   TRIGGERI
# ============================================================

RESERVE_TRIGGERS = [
    "rezerviši", "rezervisi",
    "želim da rezervišem", "zelim da rezervisem",
    "hoću da rezervišem", "hocu da rezervisem",
    "mogu da rezervišem", "mogu da rezervisem",
    "jel mogu da rezervišem", "jel mogu da rezervisem",
]

CANCEL_TRIGGERS = [
    "otkaži rezervaciju", "otkazivanje rezervacije",
    "poništi rezervaciju", "ponisti rezervaciju",
    "otkaži mesto", "otkazati mesto",
]

FREE_TRIGGERS = [
    "slobodna mesta", "ima li mesta", "koja mesta su slobodna"
]


# ============================================================
#   GLAVNA CHATBOT FUNKCIJA
# ============================================================

def find_answer(user_message: str, is_logged: bool, user_id=None) -> str:
    msg = normalize(user_message)

    if len(msg) < 2:
        return "Možeš li malo jasnije? 🙂"

    # ---------------- POZDRAVI ----------------
    if msg in ["cao", "ćao", "zdravo", "pozdrav", "hej", "hello", "hi"]:
        return "Ćao! Kako mogu da pomognem? 🙂"

    if msg in ["laku noc", "laku noć", "vidimo se", "bye"]:
        return "Vidimo se! Ako nešto zatreba, tu sam 🙂"

    # ========================================================
    # 1) PENDING MODE – već čekamo datum ili nešto
    # ========================================================
    if session.get("pending_action"):
        action = session["pending_action"]
        pending_seat = session.get("pending_seat")

        date = parse_date(user_message)
        # Osiguraj da je date objekat (pretvorimo ga ako je string)
        if isinstance(date, str):
            try:
                date = datetime.strptime(date, "%Y-%m-%d").date()
            except:
                return "Nisam uspeo da razumem datum. Unesi nešto tipa 2025-11-05 🙂"

        # ❗ Blokiraj zakazivanje prošlih datuma
        today = datetime.now().date()
        if date < today:
            return "Ne možeš rezervisati datum koji je već prošao 🙂. Unesi neki budući datum."

        if action == "reserve":
            success, message = reserve_seat(user_id, pending_seat, date)
        elif action == "cancel":
            success, message = cancel_reservation(user_id, pending_seat, date)
        elif action == "free":
            # ovde nas ne zanima pending_seat
            free = get_free_seats(date)
            session.pop("pending_action", None)
            session.pop("pending_seat", None)
            if not free:
                return f"Na datum {date} nema slobodnih mesta."
            return f"Slobodna mesta za {date}: {', '.join(map(str, free))}"

        session.pop("pending_action", None)
        session.pop("pending_seat", None)
        return message

    # ========================================================
    # 2) FULL CANCEL KOMANDA: "otkaži mesto 5 2025-12-12"
    # ========================================================
    if any(t in msg for t in CANCEL_TRIGGERS):
        if not is_logged:
            return "Da bi otkazao rezervaciju moraš biti ulogovan 🙂."

        seat_match = re.search(r"(mesto|mjesto)\s*(\d+)", msg)
        seat_number = int(seat_match.group(2)) if seat_match else None
        date = parse_date(user_message)

        if seat_number and date:
            success, message = cancel_reservation(user_id, seat_number, date)
            return message

        # ako nemamo sve informacije – idemo u korake
        if not seat_number:
            return "Koje mesto želiš da otkažeš? (npr. mesto 4)"

        session["pending_action"] = "cancel"
        session["pending_seat"] = seat_number
        return f"Za koji datum želiš da otkažeš mesto {seat_number}?"

    # ========================================================
    # 3) FULL RESERVE KOMANDA: "mesto 10 2025-12-12"
    #    ili "rezervisi mesto 5 sutra"
    # ========================================================
    # prvo tražimo broj mesta
    seat_match = re.search(r"(mesto|mjesto)\s*(\d+)", msg)
    seat_number = int(seat_match.group(2)) if seat_match else None

    # pa pokušamo da izvučemo datum iz cele poruke
    date_full = parse_date(user_message)

    # ako imamo i mesto i datum → odmah rezervišemo
    if seat_number is not None and date_full is not None:
        if not is_logged:
            return "Da bi rezervisao mesto moraš biti ulogovan 🙂."
        success, message = reserve_seat(user_id, seat_number, date_full)
        return message

    # ========================================================
    # 4) REZERVACIJA U KORACIMA
    # ========================================================
    if any(t in msg for t in RESERVE_TRIGGERS):
        if not is_logged:
            return "Da bi rezervisao mesto moraš biti ulogovan 🙂."

        # ako već u istoj poruci ima broj mesta
        if seat_number is not None:
            session["pending_action"] = "reserve"
            session["pending_seat"] = seat_number
            return f"Za koji datum želiš da rezervišeš mesto {seat_number}? (npr. sutra)"

        # ako nema broj mesta – pitamo
        return "Koje mesto želiš da rezervišeš? (npr. mesto 5)"

    # ========================================================
    # 5) SLOBODNA MESTA
    # ========================================================
    if any(t in msg for t in FREE_TRIGGERS):
        session["pending_action"] = "free"
        session["pending_seat"] = None
        return "Za koji datum želiš da proverim slobodna mesta?"

    # ========================================================
    # 6) FAQ FALLBACK
    # ========================================================
    best = None
    score = 0

    for item in FAQ_DATA:
        local = 0
        for kw in item["keywords"]:
            if kw in msg:
                local += 1
        if local > score:
            score = local
            best = item

    if best:
        return best["answer"]

    # ========================================================
    # 7) DEFAULT ODGOVOR
    # ========================================================
    return (
        "Nisam siguran da sam te razumeo 🙂\n"
        "Možeš probati, na primer:\n"
        "- rezerviši mesto 5 sutra\n"
        "- otkaži mesto 3 2025-11-05\n"
        "- slobodna mesta 2025-12-01\n"
        "- ili mi postavi bilo koje drugo pitanje 🙂"
    )


# ============================================================
#   SUGESTIJE
# ============================================================

def suggest_questions(user_message: str, limit=5):
    msg = normalize(user_message)
    suggestions = [
        item["question"]
        for item in FAQ_DATA
        if any(kw in msg for kw in item["keywords"])
    ]
    return suggestions[:limit]
