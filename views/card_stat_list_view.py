from flask import Blueprint, render_template, request, redirect, url_for, session
from services import card_stat
from services import card_list
import services.auth as auth
import traceback
from models.models import Card, Patch

bp = Blueprint("card_stat_list", __name__)

@bp.route("/card_stat_list", methods=["GET"])
def card_stat_list():
    try:
        card_stats = card_stat.get_card_stat_list()
        return render_template("card_stat_list.html", card_stats = card_stats)
    except Exception as e:
        traceback.print_exc()
        return render_template("card_stat_list.html", error_message = e)