from models.models import Card, Ability, Patch, CardWithLastPatch
from psycopg2.extensions import connection
from utils import json_card, patch_builder

def get_sql(
    search_card_id: int = None, search_name: str = None,
    cost: int = None, min_cost: int = None, max_cost: int = None,
    attack: int = None, min_attack: int = None, max_attack: int = None,
    health: int = None, min_health: int = None, max_health: int = None,
    is_active: bool = None, no_zero_id: bool = True
):
    base_sql = """
        SELECT
            card_id,
            name,
            cost,
            attack,
            health,
            image_file,
            is_active,
            ability_id,
            ability_description,
            ability_name,
            ability_image_file
        FROM card_info
    """
    conditions = []
    params = []

    if search_card_id is not None:
        conditions.append("card_id = %s")
        params.append(search_card_id)

    if search_name is not None:
        conditions.append("name LIKE %s")
        params.append(f"%{search_name}%")

    if cost is not None:
        conditions.append("cost = %s")
        params.append(cost)        

    if min_cost is not None:
        conditions.append("cost >= %s")
        params.append(min_cost)

    if max_cost is not None:
        conditions.append("cost <= %s")
        params.append(max_cost)

    if attack is not None:
        conditions.append("attack = %s")
        params.append(attack)

    if min_attack is not None:
        conditions.append("attack >= %s")
        params.append(min_attack)

    if max_attack is not None:
        conditions.append("attack <= %s")
        params.append(max_attack)

    if health is not None:
        conditions.append("health = %s")
        params.append(health)

    if min_health is not None:
        conditions.append("health >= %s")
        params.append(min_health)

    if max_health is not None:
        conditions.append("health <= %s")
        params.append(max_health)

    if is_active is not None:
        conditions.append("is_active = %s")
        params.append(is_active)

    if no_zero_id:
        conditions.append("card_id <> 0")    

    if conditions:
        sql = base_sql + " WHERE " + " AND ".join(conditions)
    else:
        sql = base_sql

    return sql, params


def card_list_builders(conn: connection,                    
    search_card_id: int = None, search_name: str = None,
    cost: int = None, min_cost: int = None, max_cost: int = None,
    attack: int = None, min_attack: int = None, max_attack: int = None,
    health: int = None, min_health: int = None, max_health: int = None,
    is_active: bool = None, no_zero_id: bool = True,
    sort_key = None, desc: bool = False):

    with conn.cursor() as cur:
        s_sql, s_params = get_sql(
            search_card_id, search_name,
            cost, min_cost, max_cost,
            attack, min_attack, max_attack,
            health, min_health, max_health,
            is_active, no_zero_id)
        cur.execute(s_sql, s_params)
        rows = cur.fetchall()
            
        cards:dict[int, Card] = {}

        for row in rows:
            card_id, name, cost, attack, health, image_file, is_active, ability_id, ability_description, ability_name, ability_image_file = row

            if card_id not in cards:
                cards[card_id] = Card(
                    card_id,
                    name,
                    cost,
                    attack,
                    health,
                    image_file,
                    is_active,
                    []
                )       

            if ability_id is not None:
                cards[card_id].abilities.append(Ability(
                    ability_id,
                    ability_name,
                    ability_description,
                    ability_image_file
                ))
                
        card_list = list(cards.values())

        if sort_key is not None:
            card_list.sort(key=sort_key)

        if desc:
            card_list.reverse()

        return card_list



def card_with_last_patch_builders(conn:connection, deck_ID):    
    with conn.cursor() as cur:
        cards: list[CardWithLastPatch] = [None] * 4    
        cur.execute("""
                    SELECT
                        dci.deck_id,
                        dci.slot,
                        dci.card_id,
                        dci.card_name,
                        dci.cost,
                        dci.attack,
                        dci.health,
                        dci.image_file,
                        dci.is_active,
                        dci.ability_id,
                        dci.ability_name,
                        dci.ability_description,
                        dci.ability_image_file,
                        cp.patch_ID
                    FROM deck_card_info AS dci
                    LEFT JOIN CardPatches AS cp
                        ON cp.card_ID = dci.card_id
                    AND cp.patch_ID = ( 
                        SELECT MAX(cp2.patch_ID)
                        FROM CardPatches AS cp2
                        WHERE cp2.card_ID = dci.card_id
                    )
                    WHERE dci.deck_id = %s;
                            """, (deck_ID,))
        
        rows = cur.fetchall()
        for deck_id, slot, card_id, card_name, cost, attack, health, image_file, is_active, ability_id, ability_name, ability_description, ability_image_file, patch_id in rows:
            if not cards[slot]:
                cards[slot] = CardWithLastPatch(
                        card = Card(
                            card_id = card_id,
                            name = card_name,
                            cost = cost,
                            attack = attack,
                            health = health,
                            image_file = image_file,
                            is_active = is_active,
                            abilities = []
                        ),
                        last_patch_id = patch_id
                    )     

            if ability_id is not None:
                cards[slot].card.abilities.append(Ability(
                    ability_id,
                    ability_name,
                    ability_description,
                    ability_image_file
                ))
            
        return cards
    


def card_slot_builders(conn:connection, deck_ID):    
    with conn.cursor() as cur:
        cards: list[Card] = [None] * 4    
        cur.execute("""
                    SELECT slot, card_id, card_name, cost, attack, health, image_file, is_active, ability_id, ability_name, ability_description, ability_image_file
                    FROM deck_card_info
                    WHERE deck_id = %s
                    ORDER BY slot;
                            """, (deck_ID,))
        rows = cur.fetchall()
        for slot, card_id, card_name, cost, attack, health, image_file, is_active, ability_id, ability_name, ability_description, ability_image_file in rows:
            if not cards[slot]:
                cards[slot] = Card(
                        card_id,
                        card_name,
                        cost,
                        attack,
                        health,
                        image_file,
                        is_active,
                        []
                    )     

            if ability_id is not None:
                cards[slot].abilities.append(Ability(
                    ability_id,
                    ability_name,
                    ability_description,
                    ability_image_file
                ))
                    
        return cards
    
def get_card_info(conn: connection, card_ID: int):
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT card_id, name, cost, attack, health, image_file, is_active, ability_id, ability_name, ability_description, ability_image_file
                    FROM card_info
                    WHERE card_id = %s
                            """, (card_ID,))
        rows = cur.fetchall()
        if not rows:
            raise ValueError(f"카드 {card_ID}가 없습니다!")
        
        first_row = rows[0]
        result_card_id, name, cost, attack, health, image_file, is_active, ability_id, ability_name, ability_description, ability_image_file = first_row
        if result_card_id != card_ID:
            raise ValueError(f"카드 검색 SQL의 결과 card_ID ({result_card_id}) 가 찾으려는 card_ID ({card_ID})와 일치하지 않습니다!")
        card = Card(
            card_id=result_card_id,
            name=name,
            cost=cost,
            attack=attack,
            health=health,
            image_file=image_file,
            is_active=is_active,
            abilities=[]
        )

        for row in rows:
            result_card_id, name, cost, attack, health, image_file, is_active, ability_id, ability_name, ability_description, ability_image_file = row
            if result_card_id != card_ID:
                raise ValueError(f"카드 검색 SQL의 결과 card_ID ({result_card_id}) 가 찾으려는 card_ID ({card_ID})와 일치하지 않습니다!")     

            if ability_id is not None:
                card.abilities.append(Ability(
                    ability_id,
                    ability_name,
                    ability_description,
                    ability_image_file
                )) 
                    
        return card
    
def get_last_patch(conn: connection, card_id: int | None = None):
            with conn.cursor() as cur:
                if card_id == 0:
                    raise ValueError("잘못된 card_ID입니다.")
                if card_id == None:
                    cur.execute("""
                            SELECT patch_ID, card_ID, before, after, changed_at, patch_user_ID 
                            FROM CardPatches
                            ORDER BY patch_ID DESC 
                            LIMIT 1
                            """)
                else:
                    cur.execute("""
                            SELECT patch_ID, card_ID, before, after, changed_at, patch_user_ID 
                            FROM CardPatches
                            WHERE card_ID = %s
                            ORDER BY patch_ID DESC 
                            LIMIT 1
                            """, (card_id,))
                row = cur.fetchone()
                result = Patch(
                    patch_ID=row[0],
                    card_ID=row[1],
                    before=json_card.json_to_card(row[2]),
                    after=json_card.json_to_card(row[3]),
                    diff_text=patch_builder.generate_diff_text(json_card.json_to_card(row[2]), json_card.json_to_card(row[3])),
                    change_at=row[4],
                    patch_user_ID=row[5]
                )
                return result