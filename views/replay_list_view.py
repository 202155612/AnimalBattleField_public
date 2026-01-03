from flask import Blueprint, render_template, request, redirect, url_for, session
from services import deck, match
from services import replay as service_replay
from services import battle as service_battle
import traceback

bp = Blueprint("replay_list", __name__)

@bp.route("/replay_list", methods=["GET"])
def replay_list():
    try:
        user_id = request.args.get("user_id")
        replays = service_replay.get_replay_list(user_id)
        return render_template("replay_list.html", replays = replays)
    except Exception as e:
        traceback.print_exc()
        return render_template("replay_list.html", replay = None, error_message=e)
