from flask import Blueprint, render_template, request, redirect, url_for, session
from services import deck, match
from services import replay as service_replay
from services import battle as service_battle
import traceback

bp = Blueprint("replay", __name__)

@bp.route("/replay", methods=["GET"])
def replay():
    try:
        match_id = request.args.get("match_id")
        replay = service_replay.get_replay(match_id)
        return render_template("replay.html", replay = replay)
    except Exception as e:
        traceback.print_exc()
        return render_template("replay.html", decks = None, error_message=e)
