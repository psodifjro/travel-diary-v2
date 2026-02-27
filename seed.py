from werkzeug.security import generate_password_hash
from app import app
from models import db, User, Trip

DEMO_TRIPS = [
    {
        "title": "Токио за 4 дня: еда, неон и спокойные парки",
        "story": "Маршрут: Асакуса → Сибуя → Мэйдзи → Одайба.\nГлавное впечатление — контраст скорости и тишины.\nСовет: берите проездной и планируйте утро для музеев.",
        "country": "Япония",
        "city": "Токио",
        "lat": 35.6762,
        "lng": 139.6503,
        "image_url": "https://images.unsplash.com/photo-1549692520-acc6669e2f0c?auto=format&fit=crop&w=1600&q=80",
        "budget": 210000,
        "safety": 5,
        "transport": 5,
        "crowd": 4,
        "nature": 3,
    },
    {
        "title": "Стамбул: чай, мосты и влюблённые коты",
        "story": "Галата → Каракёй → Султанахмет.\nУличная еда обязательна. Вечером — набережная и вид на закат.",
        "country": "Турция",
        "city": "Стамбул",
        "lat": 41.0082,
        "lng": 28.9784,
        "image_url": "https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?auto=format&fit=crop&w=1600&q=80",
        "budget": 90000,
        "safety": 4,
        "transport": 4,
        "crowd": 5,
        "nature": 2,
    },
    {
        "title": "Алтай: горные дороги и воздух, которого не хватает",
        "story": "Катунь, перевалы, вечер у костра.\nБрать тёплые вещи даже летом. Связь местами слабая — это плюс.",
        "country": "Россия",
        "city": "Горно-Алтайск",
        "lat": 51.9583,
        "lng": 85.9603,
        "image_url": "https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1600&q=80",
        "budget": 55000,
        "safety": 4,
        "transport": 3,
        "crowd": 2,
        "nature": 5,
    },
]

def main():
    with app.app_context():
        db.create_all()

        # demo user
        if not User.query.filter_by(username="demo").first():
            u = User(username="demo", password=generate_password_hash("demo"))
            db.session.add(u)
            db.session.commit()
        else:
            u = User.query.filter_by(username="demo").first()

        # add trips if none
        if Trip.query.count() == 0:
            for t in DEMO_TRIPS:
                db.session.add(Trip(user_id=u.id, **t))
            db.session.commit()

        print("Seed done. Demo user: demo / demo")

if __name__ == "__main__":
    main()