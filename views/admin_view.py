from flask import Blueprint, render_template, request, redirect, url_for
from services import auth, match
import services.battle as service_battle
from database import database as db
from utils.validators import validate_nickname, validate_password, validate_username
from flask import session
import traceback

bp = Blueprint("admin", __name__)

@bp.route("/admin", methods=["GET", "POST"])
def admin():
    try:
        if session.get("username"):
            user_info = auth.get_user_info()
            if not user_info:
                return redirect(url_for("home.home"))
            if "administrator" not in user_info.role:
                print(f"{user_info.username} is not administrator.")
                return redirect(url_for("home.home"))
        else:
            return redirect(url_for("home.home"))
        search_username = request.args.get("search_username") or ""
        search_nickname = request.args.get("search_nickname") or ""
        search_order_str = request.args.get("order") or ""
        search_order = None
        if search_order_str == "by_username":
            search_order = lambda x:x.username
        elif search_order_str == "by_nickname":
            search_order = lambda x:x.nickname
        elif search_order_str == "by_created_at":
            search_order = lambda x:x.created_at
        search_order_desc = (request.args.get("desc") == "desc") or False
        accounts = auth.get_users_list(search_username, search_nickname, search_order, search_order_desc)
        return render_template("admin.html", accounts = accounts)
    except Exception as e:
        traceback.print_exc()
        return render_template("admin.html", error_message=e)
    
        
             

        if request.method == "POST":
            user_id = request.form.get("user_id") or ""
            new_nickname = (request.form.get("new_nickname") or "").strip()
            if not user_id:
                return render_template("admin.html", error_message="사용자 이름을 입력해 주세요.")



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
    except Exception as e:
        traceback.print_exc()
        return render_template("admin.html", error_message = e)   

@bp.route("/update_nickname", methods=["POST"])
def update_nickname():
    try:
        if session.get("username"):
            user_info = auth.get_user_info()
            if not user_info:
                return redirect(url_for("home.home"))
            if "administrator" not in user_info.role:
                print(f"{user_info.username} is not administrator.")
                return redirect(url_for("home.home"))
        username = request.form.get("username").strip()
        new_nickname = request.form.get("new_nickname").strip()
        if not username:
            raise ValueError("username이 없음") 
        if not new_nickname:
            raise ValueError("new_nickname 없음") 
        if not validate_nickname(new_nickname):
            raise ValueError(f"새 nickname {new_nickname}이 적합하지 않음")
        auth.update_nickname(username, new_nickname)
        return redirect(url_for("admin.admin")) 
    except Exception as e:
        traceback.print_exc()
        return redirect(url_for("admin.admin", error_message = e))
    
@bp.route("/massive_battles", methods=["POST"])
def massive_battles():
    try:
        if session.get("username"):
            user_info = auth.get_user_info()
            if not user_info:
                return redirect(url_for("home.home"))
            if "administrator" not in user_info.role:
                print(f"{user_info.username} is not administrator.")
                return redirect(url_for("home.home"))
        for _ in range(100):
            user_id = session.get("user_ID")
            player1_deck = match.get_defense_deck_id(user_id)
            player2_deck = match.get_defense_deck_id(player1_deck.user_id)
            game = service_battle.Game(player1_deck, player2_deck)
            last_patch_id = match.get_last_patch_id()
            result = game.run(last_patch_id)
            match_id = match.insert_result(player1_deck, player2_deck, result)
        return redirect(url_for("replay_list.replay_list"))
    except Exception as e:
        traceback.print_exc()
        return redirect(url_for("admin.admin", error_message = e))
