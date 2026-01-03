from flask import Blueprint, render_template, request, redirect, url_for, session
from services import card_list, ability
import services.auth as auth
import traceback
from models.models import Card, Patch

bp = Blueprint("card_patch", __name__)

@bp.route("/card_patch", methods=["GET"])
def card_patch():
    try:
        user_id = session.get("user_ID")
        if not user_id:
            print("user_ID not valid")
            return redirect(url_for("auth.login"))
        user_role = auth.get_user_info().role
        if "developer" not in user_role:
            print(f"user_ID {user_id} is {user_role}, not developer.")
            return redirect(url_for("home.home"))
        card_infos = card_list.get_card_list()

        card_info = None

        card_info_choice = request.args.get("card_info_choice")
        ability_ids: list[int] = []
        if card_info_choice != None:
            card_info = card_list.get_card_list(search_card_id=card_info_choice)[0]
            ability_ids = [x.ability_id for x in card_info.abilities]

        abilities = ability.get_abilities()
        return render_template("card_patch.html",
                        card_infos = card_infos,
                        card = card_info,
                        ability_ids = ability_ids,
                        abilities = abilities)
    except Exception as e:
        traceback.print_exc()
        return render_template("card_patch.html",
                        error_message = e)

@bp.route("/insert_card", methods=["POST"])
def insert_card():
    try:
        user_id = session.get("user_ID")
        if not user_id:
            print("user_ID not valid")
            return redirect(url_for("auth.login"))
        user_role = auth.get_user_info().role
        if "developer" not in user_role:
            print(f"user_ID {user_id} is {user_role}, not developer.")
            return redirect(url_for("home.home"))
        card_id = card_list.insert_card(user_id)
        if not card_id:
            raise ValueError("card_ID가 정상적으로 반환되지 않았습니다.")
        return redirect(url_for("card_patch.card_patch", card_info_choice=card_id))
    except Exception as e:
        traceback.print_exc()
        return redirect(url_for("card_patch.card_patch", error_message = e))

        
@bp.route("/update_card", methods=["POST"])
def update_card():
    try:
        user_id = session.get("user_ID")
        if not user_id:
            print("user_ID not valid")
            return redirect(url_for("auth.login"))
        user_role = auth.get_user_info().role
        if "developer" not in user_role:
            print(f"user_ID {user_id} is {user_role}, not developer.")
            return redirect(url_for("home.home"))
        before_id = request.form.get("before_id", type=int)
        if before_id == None:
            raise ValueError(f"패치 전 카드 id가 없습니다.")
        card_list.update_card(
            before_id=before_id,
            card_after_update=Card(
                card_id=before_id,
                name=request.form.get("new_card_name"),
                cost=int(request.form.get("new_card_cost")),
                attack=int(request.form.get("new_card_attack")),
                health=int(request.form.get("new_card_health")),
                image_file=request.form.get("new_card_image_file"),
                is_active=('new_card_is_active' in request.form),
                abilities=ability.get_abilities(list(map(int, request.form.getlist("new_card_ability"))))
            ),
            patch_user_ID=user_id
        )
        return redirect(url_for("card_patch.card_patch", card_info_choice=before_id))
    except Exception as e:
        traceback.print_exc()
        return redirect(url_for("card_patch.card_patch", error_message = e))




@bp.route("/patch_list", methods=["GET"])
def patch_list():
    try:
        card_id = request.args.get("card_id", type=int)
        patches = card_list.get_patch_list(card_id)
        
        return render_template("patch_list.html",
                        patches = patches)

    except Exception as e:
        traceback.print_exc()
        return render_template("patch_list.html",
                        error_message = e)







'''
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
        deck_name = deck_info["deck_name"]
        is_complete = deck_info["is_complete"]
        is_defense_deck = deck_info["is_defense_deck"]
        cards = deck_info["cards"]

        return render_template("custom_deck.html",
                            deck_id = deck_id,
                            deck_name = deck_name,
                            is_complete = is_complete,
                            is_defense_deck = is_defense_deck,
                            cards = cards,
                            error_message = error_message)
    except Exception as e:
        return render_template("custom_deck.html",
                            deck_id = deck_id or "NaN",
                            deck_name = deck_name or "NaN",
                            is_complete = is_complete,
                            is_defense_deck = is_defense_deck,
                            cards = cards,
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
        deck.update_deck_status(deck_id, deck_complete)
        return redirect(url_for("deck.custom_deck", deck_id = deck_id))
    except Exception as e:
        return redirect(url_for("deck.custom_deck", deck_id = deck_id, error_message = e))

@bp.route("/<int:deck_id>/update_card", methods=["POST"])
def update_card(deck_id):
    user_id = session.get("user_ID")
    if user_id == None:
        print("user_ID not valid")
        return redirect(url_for("auth.login"))
    deck_id = request.form.get("deck_id", type=int)
    slot = request.form.get("slot", type=int)
    card_id = request.form.get("card_id", type=int)
    if deck_id == None:
        print(f"Empty deck id.")
        return redirect(url_for("home.home"))
    
    try:
        if slot == None or slot < 0:
            raise ValueError("Wrong or Empty slot")
        if card_id == None:
            raise ValueError(f"Empty card id.")
        if user_id != deck.get_deck_user_id(deck_id):
            print(f"This deck {deck_id} is not yours f{user_id}.")
            return redirect(url_for("home.home"))
        deck.update_card(deck_id, slot, card_id)
        return redirect(url_for("deck.custom_deck", deck_id=deck_id))
    except Exception as e:
        return redirect(url_for("deck.custom_deck", deck_id=deck_id, error_message = e))
    '''