from datetime import datetime
from models.models import Card, Ability

def generate_diff_text(before: Card, after: Card) -> str:
    changes = []

    if before.cost == 0 and before.attack == 0 and before.health == 0:
        changes.append(f"추가")
    else:
        if before.name != after.name:
            changes.append(f"이름: {before.name} -> {after.name}")
        if before.cost != after.cost:
            changes.append(f"비용: {before.cost} -> {after.cost}")
        if before.attack != after.attack:
            changes.append(f"공격: {before.attack} -> {after.attack}")
        if before.health != after.health:
            changes.append(f"체력: {before.health} -> {after.health}")

        before_abilities = {a.ability_id: a.name for a in before.abilities}
        after_abilities = {a.ability_id: a.name for a in after.abilities}

        for ability_id, name in after_abilities.items():
            if ability_id not in before_abilities:
                changes.append(f"({name}) 추가")
        for ability_id, name in before_abilities.items():
            if ability_id not in after_abilities:
                changes.append(f"({name}) 제거")

        if before.is_active and not after.is_active:
            changes.append(f"비활성화")

        if not before.is_active and after.is_active:
            changes.append(f"활성화")

    return "<br>".join(changes) if changes else ""
