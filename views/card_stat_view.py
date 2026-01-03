from flask import Blueprint, render_template, request, redirect, url_for, session
from services import card_stat as service_card_stat
from services import card_list
import services.auth as auth
import traceback
from models.models import Card, Patch

bp = Blueprint("card_stat", __name__)

@bp.route("/card_stat", methods=["GET"])
def card_stat_view():
    try:
        card_id = request.args.get("card_id")
        if not card_id:
            return redirect("card_stat_list.card_stat.list")
        card_stats = service_card_stat.get_card_stat_list(search_card_id=card_id)
        if len(card_stats) != 1:
            raise ValueError(f"카드 id {card_id}와 일치하는 카드가 1장이 아닙니다.")
        print(f"a f{card_stats[0]}")
        return render_template("card_stat.html", card_stat = card_stats[0])
    except Exception as e:
        traceback.print_exc()
        return render_template("card_stat.html", error_message = e)