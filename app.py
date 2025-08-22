from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from models import register_user, login_user, list_places, create_place,get_place, rate_place, upload_place_photo

app = Flask(__name__)
app.config.from_object(Config)

def current_user():
    """Devuelve el usuario actual de la sesión, si existe"""
    return session.get("user")

@app.route("/")
def index():
    if current_user():
        # Inicio con sesión iniciada
        places = list_places(limit=50).data or []
        return render_template("index_private.html", user=current_user(), places=places)
    # Inicio sin sesión
    places = list_places(limit=10).data or []
    return render_template("index_public.html", places=places)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            res = login_user(email, password)
            user = {
                "email": res.user.email,
                "id": res.user.id,
                "access_token": res.session.access_token if res.session else None,
            }
            session["user"] = user
            flash("¡Bienvenido de nuevo!", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"Error al iniciar sesión: {e}", "danger")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            res = register_user(email, password)
            flash("Cuenta creada. Revisa tu correo para confirmar.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            flash(f"No se pudo registrar: {e}", "danger")
    return render_template("register.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    flash("Sesión cerrada.", "info")
    return redirect(url_for("index"))


@app.route("/places/new", methods=["POST"])
def new_place():
    if not current_user():
        flash("Inicia sesión para publicar.", "warning")
        return redirect(url_for("login"))
    name = request.form.get("name")
    description = request.form.get("description")
    lat = request.form.get("lat", type=float)
    lng = request.form.get("lng", type=float)

    photo_url = None
    file = request.files.get("photo")
    if file and file.filename:
        # sube a Supabase Storage
        file_bytes = file.read()
        photo_url = upload_place_photo(file_bytes, f"{current_user()['id']}_{file.filename}")

    create_place(current_user()["id"], name, description, lat, lng, photo_url)
    flash("Puesto publicado.", "success")
    return redirect(url_for("index"))


@app.route("/places/<place_id>/rate", methods=["POST"])
def rate(place_id):
    if not current_user():
        flash("Inicia sesión para calificar.", "warning")
        return redirect(url_for("login"))
    rating = request.form.get("rating", type=int)
    comment = request.form.get("comment")
    rate_place(place_id, current_user()["id"], rating, comment)
    flash("¡Gracias por tu opinión!", "success")
    return redirect(url_for("index"))


@app.route("/places/<place_id>")
def place_detail(place_id):
    data = get_place(place_id).data
    if not data:
        flash("Puesto no encontrado.", "warning")
        return redirect(url_for("index"))
    return render_template("place_detail.html", place=data)


if __name__ == "__main__":
    app.run(debug=True)
