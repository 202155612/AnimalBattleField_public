from models.models import Card, Ability
from dataclasses import dataclass, asdict, field
import json

def card_to_json(card: Card) -> str:
    return json.dumps(asdict(card), ensure_ascii=False, indent=4)


def json_to_card(data: dict) -> Card:
    abilities_data = data.get("abilities", [])
    abilities = [Ability(**ability_dict) for ability_dict in abilities_data]

    return Card(
        card_id=data["card_id"],
        name=data["name"],
        cost=data["cost"],
        attack=data["attack"],
        health=data["health"],
        image_file=data["image_file"],
        abilities=abilities,
        is_active=data["is_active"]
    )