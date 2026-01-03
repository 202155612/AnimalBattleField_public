from flask import Blueprint, render_template, request, redirect, url_for
import services.auth as auth

bp = Blueprint("account", __name__)

@bp.route("/account")
def account():
    user_info = auth.get_user_info()
    if not user_info:
        return redirect(url_for("auth.login"))
    return render_template("account.html", 
                           username = user_info.username, 
                           nickname = user_info.nickname, 
                           created_at = user_info.created_at,
                           role = ", ".join(user_info.role) if user_info.role else "No Role")