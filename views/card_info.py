from flask import Blueprint, render_template, request, redirect, url_for
import services.card_info as card_info_service

bp = Blueprint("card_info", __name__)

@bp.route("/card_info")
def card_info():
    card_info = card_info_service.get_card_info(request.args.get("card_id", type=int))
    if not card_info:
        return redirect(url_for("auth.login"))
    return render_template("card_info.html", 
                           card_name = card_info["card_name"], 
                           description = card_info["description"], 
                           cost = card_info["cost"],
                           attack = card_info["attack"],
                           health = card_info["health"])