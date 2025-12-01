import re

FAQ = [
    {
        "question": "Koje je radno vreme čitaonice?",
        "answer": "Radno vreme čitaonice je radnim danima od 08:00 do 22:00, a vikendom od 10:00 do 18:00.",
        "keywords": ["radno vreme", "radno", "vreme", "otvoreno", "kada radi", "dokle radi"]
    },
    {
        "question": "Kako mogu da rezervišem mesto u čitaonici?",
        "answer": "Mesto u čitaonici se može rezervisati putem studentskog portala ili na info-pultu lično.",
        "keywords": ["rezervacija", "rezervisati", "rezervisem", "rezervišem", "zakazati", "mesto", "sto", "stol"]
    },
    {
        "question": "Da li postoji članarina za čitaonicu?",
        "answer": "Korišćenje čitaonice je besplatno za studente fakulteta, a za ostale korisnike se plaća simbolična članarina.",
        "keywords": ["clanarina", "članarina", "placa", "plaća", "uplata", "besplatno"]
    },
    {
        "question": "Da li se knjige mogu iznositi iz čitaonice?",
        "answer": "Knjige se u pravilu ne iznose iz čitaonice, osim u slučaju kada je to posebno naznačeno.",
        "keywords": ["knjige", "iznositi", "poneti", "iznosi", "pozajmica", "pozajmljivanje"]
    },
    {
        "question": "Kako da postanem član čitaonice?",
        "answer": "Član čitaonice možeš postati popunjavanjem pristupnice na info-pultu uz indeks ili ličnu kartu.",
        "keywords": ["uclanjenje", "učlanjenje", "postanem član", "postati clan", "pristupnica"]
    }
    # ... i ostala pitanja (samo ih kopiraš od gore)
]


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\wšđčćž ]", " ", text)
    return text


def find_answer(user_message: str) -> str:
    msg = normalize(user_message)
    words = msg.split()

    GREETINGS = ["cao", "ćao", "zdravo", "hej", "hello", "hi", "pozdrav"]
    for g in GREETINGS:
        if g in msg:
            return "Ćao! Kako mogu da ti pomognem? 😊"

    THANKS = ["hvala", "hvalaaa", "tnx", "thx"]
    for t in THANKS:
        if t in msg:
            return "Nema na čemu! Tu sam ako ti još nešto treba 😊"

    GOODBYE = ["vidimo se", "idem", "odlazim", "laku noć", "laku noc"]
    for bye in GOODBYE:
        if bye in msg:
            return "Vidimo se! 👋"

    if "ko si ti" in msg:
        return "Ja sam chatbot čitaonice! Tu sam da ti pomognem 😊"

    best_match = None
    best_score = 0

    for item in FAQ:
        score = 0
        for kw in item["keywords"]:
            kw_norm = normalize(kw)
            if kw_norm in msg:
                score += 2
            for w in kw_norm.split():
                if w in words:
                    score += 1

        if score > best_score:
            best_score = score
            best_match = item

    if best_score == 0:
        return "Trenutno nemam odgovor na ovo pitanje. Pokušaj malo drugačije 🙂."

    return best_match["answer"]


def suggest_questions(user_message: str, limit=5):
    msg = normalize(user_message)
    words = msg.split()
    scored = []

    for item in FAQ:
        score = 0
        for kw in item["keywords"]:
            kw_norm = normalize(kw)
            if kw_norm in msg:
                score += 2
            for w in kw_norm.split():
                if w in words:
                    score += 1

        if score > 0:
            scored.append((score, item["question"]))

    scored.sort(reverse=True)

    suggestions = []
    for _, q in scored:
        if q not in suggestions:
            suggestions.append(q)
        if len(suggestions) >= limit:
            break

    if not suggestions:
        suggestions = [item["question"] for item in FAQ[:limit]]

    return suggestions
