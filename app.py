from flask import Flask, jsonify, render_template, redirect, url_for, request, flash
import requests
import os
from database import db, create_all, User as UserModel, Ressources
from dotenv import load_dotenv
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from src.constants import RESSOURCE_SCHEMA
from src.forms import RessourceForm, LoginForm, RegistrationForm, PasswordResetForm
from flask_bootstrap import Bootstrap5
from flask_caching import Cache
import json
from functools import wraps
from flask_rebar import Rebar
from src.utils import get_missing_fields, get_ressources

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
login_manager = LoginManager()
login_manager.init_app(app)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URI")
db.init_app(app)
AUTH_URL = os.getenv("AUTH_URL")
bootstrap = Bootstrap5(app)
cache = Cache(config={"CACHE_TYPE": "SimpleCache"})
cache.init_app(app)
rebar = Rebar()
api_v1_registry = rebar.create_handler_registry(prefix='/api/v1')


class User(UserMixin, UserModel):
    pass


with app.app_context():
    create_all(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = User.query.filter_by(id=current_user.id).first()
        if not user.admin:
            flash("You do not have the necessary permissions to complete this request. Admin access is required.", "error")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function

def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = requests.get(url=f"{AUTH_URL}/apikey/verify", headers=request.headers)
        if response.status_code != 200:
            return response.json()['message']
        request.user_id = response.json()['user_id']
        return f(*args, **kwargs)
    return decorated_function 

@app.route("/", methods=["GET", "POST"])
def home():
    search_query = []
    if request.method == 'POST':
        search_query = [arg.strip().lower() for arg in request.form.get('search').split(",")]
        ressources = get_ressources(Ressources, filter=search_query)
    else:
        ressources = get_ressources(Ressources, cache=cache)

    user_ids = [ressource.user_id for ressource in ressources]
    users = User.query.filter(User.id.in_(user_ids)).all()
    user_dict = {user.id: user.username for user in users}
    filtered_ressources = []
    for ressource in ressources:
        if not current_user.is_authenticated and ressource.private:
            continue
        ressource.username = user_dict.get(ressource.user_id, "-")
        filtered_ressources.append(ressource)

        
    return render_template("index.html", ressources=filtered_ressources, search_query=" ".join(search_query))


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if not user.admin:
            flash("You do not have the necessary permissions to login. Admin access is required.", "error")
            return redirect(url_for("home"))
        data = {
            "email": email,
            "password": password
        }
        response = requests.post(url=f"{AUTH_URL}/login", json=data)
        if response.status_code == 200:
            flash(response.json()['message'], "success")
            login_user(user)
            return redirect(url_for("home"))
        flash(response.json()['message'], "error")
        
    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        username = form.username.data
        data = {
            "email": email,
            "password": password,
            "username": username,
            "then": "https://library.timonrieger.de/login"
        }
        response = requests.post(f"{AUTH_URL}/register", json=data)
        flash(response.json()['message'], "success") if response.status_code == 200 else flash(response.json()['message'], "error")
        
    return render_template("register.html", form=form)


@app.route("/reset", methods=["GET", "POST"])
def reset():
    form = PasswordResetForm()
    
    if form.validate_on_submit():
        email = form.email.data
        data = {
            "email": email,
            "then": "https://library.timonrieger.de/login"
        }
        response = requests.post(url=f"{AUTH_URL}/reset", json=data)
        flash(response.json()['message'], "success") if response.status_code == 200 else flash(response.json()['message'], "error")
        
    return render_template("reset.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out", "success")
    return redirect(url_for("home"))


@app.route("/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit():
    id = request.args.get("id")
    form = RessourceForm()
    ressource = Ressources.query.filter_by(id=id).first()
    
    if form.validate_on_submit():
        ressource.name = form.name.data
        ressource.link = form.link.data
        ressource.medium = form.medium.data
        ressource.category = form.category.data
        ressource.tags = json.dumps(form.tags.data)
        ressource.description=form.description.data
        ressource.private = True if form.private.data == "True" else False
        db.session.commit()
        cache.clear()
        flash("Ressource updated successfully", "success")
        return redirect(url_for("home"))
    
    if ressource:
        form = RessourceForm(
            name=ressource.name,
            link=ressource.link,
            medium=ressource.medium,
            category=ressource.category,
            tags=json.loads(ressource.tags),
            description=ressource.description,
            private=ressource.private
        )
    return render_template("add.html", form=form, id=id, edit=True, ressource=ressource.name)


@app.route("/delete")
@login_required
@admin_required
def delete():
    id = request.args.get("id")
    ressource = Ressources.query.filter_by(id=id).first()
    form = RessourceForm(
        name=ressource.name,
        link=ressource.link,
        medium=ressource.medium,
        category=ressource.category,
        tags=json.loads(ressource.tags),
        description=ressource.description,
        private=ressource.private
    )
    db.session.delete(ressource)
    db.session.commit()
    cache.clear()
    flash("Ressource deleted successfully. Accident? Add the ressource again by submitting the form.", "success")
    return render_template("add.html", form=form)


@app.route("/add", methods=["GET", "POST"])
@login_required
@admin_required
def add():
    form = RessourceForm()
    
    if form.validate_on_submit():
        already_exists = Ressources.query.filter_by(link=form.link.data).first()
        if already_exists:
            flash("Ressource already exists", "error")
        else:
            ressource = Ressources(
                name=form.name.data,
                link=form.link.data,
                medium=form.medium.data,
                category=form.category.data,
                tags=json.dumps(form.tags.data),
                user_id=current_user.id,
                description=form.description.data,
                private=True if form.private.data == "True" else False
            )
            db.session.add(ressource)
            db.session.commit()
            cache.clear()
            flash("Ressource added successfully", "success")
            return redirect(url_for("home"))

    return render_template("add.html", form=form)

@api_v1_registry.handles(rule="/ressources", method="GET")
def api_get_ressources():
    query = [arg.strip().lower() for arg in request.args.get("q").split(",")] if request.args.get("q") else None
    if query:
        data = get_ressources(ressource_model=Ressources, filter=query)
    else:
        data = get_ressources(ressource_model=Ressources, cache=cache)
    return [ressource.to_dict() for ressource in data]

@api_v1_registry.handles(rule="/ressources", method="POST")
@api_key_required
def api_post_ressource():
    data = request.get_json()
    required_fields = RESSOURCE_SCHEMA['required']
    if not data or get_missing_fields(data, required_fields):
        return jsonify({'message': f"Missing field(s): {', '.join(get_missing_fields(data, required_fields))}"}), 400

    already_exists = Ressources.query.filter_by(link=data["link"]).first()
    if already_exists:
        return jsonify({"error": "Ressource already exists"}), 409
    ressource = Ressources(
        name=data["name"],
        link=data["link"],
        medium=data.get("medium"),
        category=data.get("category"),
        tags=json.dumps(data.get("tags", [])),
        user_id=request.user_id,
        description=data.get("description", ""),
        private=True if data.get("private") == "true" else False
    )
    db.session.add(ressource)
    db.session.commit()
    cache.clear()

    return jsonify({"message": "Ressource added successfully", "data": ressource.to_dict()}), 201

if __name__ == '__main__':
    rebar.init_app(app)
    app.run(debug=False)