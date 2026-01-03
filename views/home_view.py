from flask import Blueprint, render_template, redirect, url_for, request, session
import database.database as database
from services import auth

bp = Blueprint("home", __name__)


@bp.route("/")
def entrance():
    return redirect(url_for("home.home"))

@bp.route("/home")
def home():
    try:
        account = auth.get_user_info()
        if account:
            return render_template("index.html", account = account)
        else:
            return render_template("index.html")
    except Exception as e:
        return render_template("index.html", error_message = e)
    

@bp.route("/logout", methods=["POST"])
def logout_route():
    database.logout()
    return redirect(url_for("home.home"))