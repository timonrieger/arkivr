from flask import Flask, render_template, redirect, url_for, request, flash
import requests
import os
from database import db, create_all, User as UserModel, Ressources
from dotenv import load_dotenv
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from sqlalchemy import or_
from src.admins import ADMINS
from src.forms import RessourceForm, LoginForm, RegistrationForm
from flask_bootstrap import Bootstrap5
import json

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
login_manager = LoginManager()
login_manager.init_app(app)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URI")
db.init_app(app)
AUTH_URL = os.getenv("AUTH_URL")
bootstrap = Bootstrap5(app)
app.jinja_env.filters['zip'] = zip

app.logger.setLevel("INFO")

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


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == 'POST':
        search_query = [arg.strip().lower() for arg in request.form.get('search').split(",")]
        search_filters = []
        for search_arg in search_query:
            search_filters.append(
                or_(
                    Ressources.name.ilike(f"%{search_arg}%"),
                    Ressources.description.ilike(f"%{search_arg}%"),
                    Ressources.category.ilike(f"%{search_arg}%"),
                    Ressources.topic.ilike(f"%{search_arg}%"),
                    Ressources.tags.ilike(f"%{search_arg}%"),
                    Ressources.medium.ilike(f"%{search_arg}%"),
                    Ressources.link.ilike(f"%{search_arg}%"),
                )
            )
        ressources = Ressources.query.filter(or_(*search_filters)).all()
        for ressource in ressources:
            user = User.query.filter_by(id=ressource.user_id).first()
            ressource.username = user.username if user else "-"
        
        return render_template("index.html", ressources=ressources, search_query=" ".join(search_query))
        
    ressources = Ressources.query.all()
    for ressource in ressources:
        user = User.query.filter_by(id=ressource.user_id).first()
        ressource.username = user.username if user else "-"
        
    return render_template("index.html", ressources=ressources)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        if request.form['email'] not in ADMINS:
            flash("You are not allowed to login.", "error")
            return redirect(url_for("home"))
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        response = requests.post(url=f"{AUTH_URL}/login?email={email}&password={password}")
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
        if request.form['email'] not in ADMINS:
            flash("You are not allowed to register.", "error")
            return redirect(url_for("home"))
        email = request.form["email"]
        password = request.form["password"]
        username = request.form["username"]
        response = requests.post(url=f"{AUTH_URL}/register?email={email}&password={password}&username={username}&then=https://filmhub.timonrieger.de/")
        if response.status_code == 200:
            flash(response.json()['message'], "success")
            user = User.query.filter_by(email=email).first()
            login_user(user)
            return redirect(url_for("home"))
        flash(response.json()['message'], "error")
        
    return render_template("register.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out", "success")
    return redirect(url_for("home"))


@app.route("/edit", methods=["GET", "POST"])
@login_required
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
            description=ressource.description
        )
    return render_template("add.html", form=form, id=id, edit=True)


@app.route("/delete")
@login_required
def delete():
    id = request.args.get("id")
    ressource = Ressources.query.filter_by(id=id).first()
    db.session.delete(ressource)
    db.session.commit()
    flash("Ressource deleted successfully", "success")
    return redirect(url_for("home"))


@app.route("/add", methods=["GET", "POST"])
@login_required
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
                description=form.description.data
            )
            db.session.add(ressource)
            db.session.commit()
            flash("Ressource added successfully", "success")
            return redirect(url_for("home"))

    return render_template("add.html", form=form)


if __name__ == '__main__':
    app.run(debug=False)
