from flask import Blueprint, render_template, request, redirect, url_for
import services.auth as auth
from database import database as db
from utils.validators import validate_nickname, validate_password, validate_username
from flask import session

bp = Blueprint("auth", __name__)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("username"):
        try:
            if auth.get_user_info():
                return redirect(url_for("home.home"))
        except Exception as e:
            print(e)
            db.logout()          

    if request.method == "POST":
        u = (request.form.get("username") or "").strip()
        p = (request.form.get("password") or "").strip()
        if not u:
            return render_template("login.html", error_message="사용자 이름을 입력해 주세요.")
        if not validate_username(u):
            return render_template("login.html", error_message="사용자 이름 형식이 올바르지 않습니다.")
        if not p:
            return render_template("login.html", error_message="비밀번호를 입력해 주세요.")
        if not validate_password(p):
            return render_template("login.html", error_message="비밀번호 형식이 올바르지 않습니다.")
        try:
            if auth.login(u, p):
                return redirect(url_for("home.home"))
        except Exception as e:
            return render_template("login.html", error_message=str(e))         
        return render_template("login.html", error_message="잘못된 로그인입니다.")
    return render_template("login.html", error_message=None)

@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        n = request.form.get("nickname").strip()
        u = request.form.get("username").strip()
        p = request.form.get("password").strip()
        if not u:
            return render_template("register.html", error_message="사용자 이름을 입력해 주세요.")
        if not validate_username(u):
            return render_template("register.html", error_message="사용자 이름 형식이 올바르지 않습니다.")
        if not p:
            return render_template("register.html", error_message="비밀번호를 입력해 주세요.")
        if not validate_password(p):
            return render_template("register.html", error_message="비밀번호 형식이 올바르지 않습니다.")
        if not n:
            return render_template("register.html", error_message="닉네임을 입력해 주세요.")
        if not validate_nickname(n):
            return render_template("register.html", error_message="닉네임 형식이 올바르지 않습니다.")
        try:
            if auth.register(u, p, n):
                return redirect(url_for("home.home"))
            else:
                return render_template("register.html", error_message="이미 존재하는 사용자 이름입니다.")
        except Exception as e:
            return render_template("register.html", error_message=str(e))
    return render_template("register.html", error_message = None)