from flask import Blueprint, render_template, request, redirect, url_for, session
from services import deck
from services import card_list
import json

bp = Blueprint("deck", __name__)

@bp.route("/create_deck", methods=["GET", "POST"])
def create_deck():
    try:
        if request.method == "POST":
            user_id = session.get("user_ID")
            if not user_id:
                print("user_ID not valid")
                return redirect(url_for("auth.login"))
            deck_name = request.form.get("deck_name")
            if not deck_name:
                return render_template("create_deck.html")
            deck_id = deck.create_deck(user_id, deck_name)
            return redirect(url_for("deck.custom_deck", deck_id = deck_id))
        return render_template("create_deck.html")
    except Exception as e:
        return render_template("create_deck.html", error_message=e)

@bp.route("/custom_deck")
def custom_deck():
    user_id = session.get("user_ID")
    if not user_id:
        print("user_ID not valid")
        return redirect(url_for("auth.login"))
    deck_id = request.args.get("deck_id", type=int)
    if not deck_id:
        print("no deck id")
        return redirect(url_for("home.home"))
    if user_id != deck.get_deck_user_id(deck_id):
        print(f"deck {deck_id} is not for user {user_id}")
        return redirect(url_for("home.home"))
    
    error_message = request.args.get("error_message", type=str)

    try:
        deck_info = deck.get_deck_info(deck_id)
        if deck_info == None:
            raise ValueError(f"{deck_id} 덱이 없습니다!")
        cards = card_list.get_card_list(key = lambda x:x.cost)

        return render_template("custom_deck.html",
                            deck=deck_info, cards = cards, error_message = error_message)
    except Exception as e:
        return render_template("custom_deck.html",
                            error_message=e)

@bp.route("/<int:deck_id>/update_name", methods=["POST"])
def update_name(deck_id):
    user_id = session.get("user_ID")
    if not user_id:
        print("user_ID not valid")
        return redirect(url_for("auth.login"))
    if not deck_id:
        print("no deck id")
        return redirect(url_for("home.home"))
    if user_id != deck.get_deck_user_id(deck_id):
        print(f"deck {deck_id} is not for user {user_id}")
        return redirect(url_for("home.home"))
    
    try:
        new_deck_name = request.form.get("deck_name")
        if not new_deck_name.strip():
            raise ValueError("덱 이름이 비어 있습니다.")
        deck.update_deck_name(deck_id, new_deck_name)
        return redirect(url_for("deck.custom_deck", deck_id = deck_id))
    except Exception as e:
        return redirect(url_for("deck.custom_deck", deck_id = deck_id, error_message = e))


@bp.route("/<int:deck_id>/update_status", methods=["POST"])
def update_status(deck_id):
    user_id = session.get("user_ID")
    if not user_id:
        print("user_ID not valid")
        return redirect(url_for("auth.login"))
    if not deck_id:
        print("no deck id")
        return redirect(url_for("home.home"))
    if user_id != deck.get_deck_user_id(deck_id):
        print(f"deck {deck_id} is not for user {user_id}")
        return redirect(url_for("home.home"))
    
    try:
        deck_complete = request.form.get("deck_complete")
        if not deck_complete:
            raise ValueError("변경값이 비어 있습니다.")
        card_ids_json = request.form.get("card_ids_json")
        if not card_ids_json:
            raise ValueError("카드 정보가 없습니다.")
        raw_list = json.loads(card_ids_json)
        if not isinstance(raw_list, list):
            raise ValueError("카드 정보 형식이 잘못되었습니다.")
        card_ids = []
        for v in raw_list:
            if v is None:
                card_ids.append(None)
            else:
                card_ids.append(int(v))

        if len(card_ids) != 4:
            raise ValueError("카드는 4장이어야 합니다.")

        deck.update_card(deck_id, card_ids)
        deck.update_deck_status(deck_id, deck_complete)

        return redirect(url_for("deck.custom_deck", deck_id=deck_id))
    except Exception as e:
        return redirect(url_for("deck.custom_deck", deck_id=deck_id, error_message=e))