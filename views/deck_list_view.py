from flask import Blueprint, render_template, request, redirect, url_for
import services.deck as deck
from flask import session


bp = Blueprint("deck_list", __name__)

@bp.route("/deck_list")
def deck_list():
    user_ID = session.get("user_ID")
    if not user_ID:
        return redirect(url_for("auth.login"))
    return render_template("deck_list.html", 
                           decks = deck.get_deck_list(user_ID))