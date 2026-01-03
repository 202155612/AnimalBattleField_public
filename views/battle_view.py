from flask import Blueprint, render_template, request, redirect, url_for, session
from services import deck, match
from services import battle as service_battle
import traceback

bp = Blueprint("battle", __name__)

@bp.route("/choose_deck", methods=["GET"])
def choose_deck():
    user_id = session.get("user_ID")
    if not user_id:
        print("user_ID not valid")
        return redirect(url_for("auth.login"))
    try:
        decks = deck.get_deck_list(user_id, only_complete=True)
        return render_template("choose_deck.html", decks = decks)
    except Exception as e:
        traceback.print_exc()
        return render_template("choose_deck.html", decks = None, error_message=e)

@bp.route("/battle", methods=["POST"])
def battle():
    user_id = session.get("user_ID")
    if user_id == None:
        print("user_ID not valid")
        return redirect(url_for("auth.login"))
    deck_id = request.form.get("rep_deck_id", type=int)
    if deck_id == None:
        return redirect(url_for("battle.choose_deck"))
    if deck.get_deck_user_id(deck_id) != user_id:
        raise ValueError(f"deck ID {deck_id}의 소유자가 user id {user_id}가 아닙니다.")
    try:
        enemy_deck = match.get_defense_deck_id(user_id)
        my_deck = deck.get_deck_info_with_last_patches(deck_id)
        game = service_battle.Game(my_deck, enemy_deck)
        last_patch_id = match.get_last_patch_id()
        result = game.run(last_patch_id)
        match_id = match.insert_result(my_deck, enemy_deck, result)
        return redirect(url_for("replay.replay", match_id = match_id))
    except Exception as e:
        traceback.print_exc()
        return render_template("choose_deck.html", decks = None, error_message=e)
    
    