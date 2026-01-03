from flask import Blueprint, render_template, request, redirect, url_for
import services.card_list as card_list_service

bp = Blueprint("card_list", __name__)

@bp.route("/card_list")
def card_list():
    search_card_id = request.args.get("card_id", type=int)
    search_name = request.args.get("card_name", type=str)

    cost = None
    min_cost = None
    max_cost = None
    attack = None
    min_attack = None
    max_attack = None
    health = None
    min_health = None
    max_health = None

    if request.args.get("costEnabled"):
        if request.args.get("costMode", type=str) == "single":
            cost = request.args.get("cost", type=int)
        else:
            min_cost = request.args.get("costMin", type=int)
            max_cost = request.args.get("costMax", type=int)

    if request.args.get("attackEnabled"):
        if request.args.get("attackMode", type=str) == "single":
            attack = request.args.get("attack", type=int)
        else:
            min_attack = request.args.get("attackMin", type=int)
            max_attack = request.args.get("attackMax", type=int)

    if request.args.get("healthEnabled"):
        if request.args.get("healthMode", type=str) == "single":
            health = request.args.get("health", type=int)
        else:
            min_health = request.args.get("healthMin", type=int)
            max_health = request.args.get("healthMax", type=int)


    order: str | None = request.args.get("order")
    key = None
    if order:
        if order == "by_id":
            key = lambda x: x.card_id
        elif order == "by_name":
            key = lambda x: x.name
        elif order == "by_cost":
            key = lambda x: x.cost
        elif order == "by_attack":
            key = lambda x: x.attack
        elif order == "by_health":
            key = lambda x: x.health
    
    desc = (request.args.get("desc") == "desc")
        
    card_list = card_list_service.get_card_list(
        search_card_id=search_card_id,
        search_name=search_name,
        cost=cost,
        min_cost=min_cost,
        max_cost=max_cost,
        attack=attack,
        min_attack=min_attack,
        max_attack=max_attack,
        health=health,
        min_health=min_health,
        max_health=max_health,
        is_active=True,
        key=key,
        desc=desc
    )

    return render_template("card_list.html", cards=card_list)
