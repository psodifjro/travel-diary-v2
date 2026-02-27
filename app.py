import os
from flask import Flask, render_template, redirect, url_for, request, abort, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user

from models import db, User, Trip


app = Flask(__name__)
app.config["SECRET_KEY"] = "travel-diary-v2-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///travel.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()


@app.route("/")
def dashboard():
    """
    Главная страница = "Дашборд":
    - свежие путешествия
    - короткая статистика
    - подборка "Сегодня в вдохновении"
    """
    latest = Trip.query.order_by(Trip.created_at.desc()).limit(10).all()
    total_trips = Trip.query.count()
    total_users = User.query.count()
    my_trips = Trip.query.filter_by(user_id=current_user.id).count() if current_user.is_authenticated else 0

    featured = Trip.query.order_by(Trip.budget.desc()).first()  # простая "витрина": самое дорогое

    return render_template(
        "dashboard.html",
        latest=latest,
        total_trips=total_trips,
        total_users=total_users,
        my_trips=my_trips,
        featured=featured
    )


@app.route("/explore")
def explore():
    """
    Просмотр путешествий других пользователей (и своих тоже, если хочется).
    Фильтрация по стране/городу + сортировка.
    """
    country = request.args.get("country", "").strip()
    city = request.args.get("city", "").strip()
    sort = request.args.get("sort", "new")  # new | budget | safety

    q = Trip.query
    if country:
        q = q.filter(Trip.country.ilike(f"%{country}%"))
    if city:
        q = q.filter(Trip.city.ilike(f"%{city}%"))

    if sort == "budget":
        q = q.order_by(Trip.budget.desc())
    elif sort == "safety":
        q = q.order_by(Trip.safety.desc(), Trip.created_at.desc())
    else:
        q = q.order_by(Trip.created_at.desc())

    trips = q.all()
    return render_template("explore.html", trips=trips, country=country, city=city, sort=sort)


@app.route("/trip/<int:trip_id>")
def trip(trip_id):
    t = Trip.query.get_or_404(trip_id)
    return render_template("trip.html", t=t)


@app.route("/create", methods=["GET", "POST"])
@login_required
def create_trip():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        story = request.form.get("story", "").strip()
        country = request.form.get("country", "").strip()
        city = request.form.get("city", "").strip()

        image_url = request.form.get("image_url", "").strip()
        budget = int(request.form.get("budget", "0") or 0)

        lat_val = request.form.get("lat", "").strip()
        lng_val = request.form.get("lng", "").strip()
        lat = float(lat_val) if lat_val else None
        lng = float(lng_val) if lng_val else None

        safety = int(request.form.get("safety", "3"))
        transport = int(request.form.get("transport", "3"))
        crowd = int(request.form.get("crowd", "3"))
        nature = int(request.form.get("nature", "3"))

        if not title or not story or not country or not city:
            flash("Заполните обязательные поля: название, текст, страна, город", "danger")
            return redirect(url_for("create_trip"))

        t = Trip(
            title=title,
            story=story,
            country=country,
            city=city,
            lat=lat,
            lng=lng,
            image_url=image_url,
            budget=budget,
            safety=safety,
            transport=transport,
            crowd=crowd,
            nature=nature,
            user_id=current_user.id,
        )
        db.session.add(t)
        db.session.commit()

        flash("Путешествие сохранено!", "success")
        return redirect(url_for("profile", user_id=current_user.id))

    return render_template("create_trip.html")


@app.route("/profile/<int:user_id>")
def profile(user_id):
    u = User.query.get_or_404(user_id)
    trips = Trip.query.filter_by(user_id=u.id).order_by(Trip.created_at.desc()).all()

    total_budget = sum([t.budget for t in trips]) if trips else 0
    avg_safety = round(sum([t.safety for t in trips]) / len(trips), 2) if trips else 0

    return render_template("profile.html", u=u, trips=trips, total_budget=total_budget, avg_safety=avg_safety)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Заполните логин и пароль", "danger")
            return redirect(url_for("register"))

        if User.query.filter_by(username=username).first():
            flash("Пользователь уже существует", "danger")
            return redirect(url_for("register"))

        u = User(username=username, password=generate_password_hash(password))
        db.session.add(u)
        db.session.commit()

        flash("Регистрация успешна! Теперь войдите.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        u = User.query.filter_by(username=username).first()
        if not u or not check_password_hash(u.password, password):
            flash("Неверный логин или пароль", "danger")
            return redirect(url_for("login"))

        login_user(u)
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    # 5001 чтобы не конфликтовать с macOS (порт 5000 часто занят)
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)