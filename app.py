from flask import Flask, render_template, redirect, url_for, request, flash
import requests
import os
from database import db, create_all, User as UserModel, Ressources
from dotenv import load_dotenv
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from sqlalchemy import or_
from src.forms import RessourceForm, LoginForm, RegistrationForm, PasswordResetForm
from flask_bootstrap import Bootstrap5
import json
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
login_manager = LoginManager()
login_manager.init_app(app)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URI")
db.init_app(app)
AUTH_URL = os.getenv("AUTH_URL")
bootstrap = Bootstrap5(app)


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


@app.route("/", methods=["GET", "POST"])
def home():
    search_query = []
    if request.method == 'POST':
        search_query = [arg.strip().lower() for arg in request.form.get('search').split(",")]
        search_filters = [
            or_(
                Ressources.name.ilike(f"%{search_arg}%"),
                Ressources.description.ilike(f"%{search_arg}%"),
                Ressources.category.ilike(f"%{search_arg}%"),
                Ressources.topic.ilike(f"%{search_arg}%"),
                Ressources.tags.ilike(f"%{search_arg}%"),
                Ressources.medium.ilike(f"%{search_arg}%"),
                Ressources.link.ilike(f"%{search_arg}%"),
            ) for search_arg in search_query
        ]
        ressources = Ressources.query.filter(or_(*search_filters)).all()
    else:
        ressources = Ressources.query.all()

    filtered_ressources = []
    for ressource in ressources:
        if not current_user.is_authenticated and ressource.private:
            continue
        user = User.query.filter_by(id=ressource.user_id).first()
        ressource.username = user.username if user else "-"
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
        ressource.topic = form.topic.data
        ressource.tags = json.dumps(form.tags.data)
        ressource.description=form.description.data
        ressource.private = True if form.private.data == "True" else False
        db.session.commit()
        flash("Ressource updated successfully", "success")
        return redirect(url_for("home"))
    
    if ressource:
        form = RessourceForm(
            name=ressource.name,
            link=ressource.link,
            medium=ressource.medium,
            category=ressource.category,
            topic=ressource.topic,
            tags=json.loads(ressource.tags),
            description=ressource.description,
            private=ressource.private
        )
    return render_template("add.html", form=form, id=id, edit=True)


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
        topic=ressource.topic,
        tags=json.loads(ressource.tags),
        description=ressource.description,
        private=ressource.private
    )
    db.session.delete(ressource)
    db.session.commit()
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
                topic=form.topic.data,
                tags=json.dumps(form.tags.data),
                user_id=current_user.id,
                description=form.description.data,
                private=True if form.private.data == "True" else False
            )
            db.session.add(ressource)
            db.session.commit()
            flash("Ressource added successfully", "success")
            return redirect(url_for("home"))

    return render_template("add.html", form=form)


if __name__ == '__main__':
    app.run(debug=True)
