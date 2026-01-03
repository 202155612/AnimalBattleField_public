import psycopg2
import database.database as db
from repo import repo_card, repo_deck
from models.models import Card, Patch
from utils import json_card, patch_builder


def get_card_list(
    search_card_id: int = None, search_name: str = None,
    cost: int = None, min_cost: int = None, max_cost: int = None,
    attack:int = None, min_attack: int = None, max_attack: int = None,
    health: int = None, min_health: int = None, max_health: int = None,
    is_active: bool = None, no_zero_id: bool = True, key = None, desc: bool = False
):
    conn = None
    try:
        conn = db.access()
        with conn:
            cards = repo_card.card_list_builders(conn, search_card_id, search_name, 
                                                     cost, min_cost, max_cost,
                                                     attack, min_attack, max_attack,
                                                     health, min_health, max_health,
                                                     is_active, no_zero_id, key, desc
                                                     )
            return cards

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None

    finally:
        if conn is not None:
            conn.close()

def insert_card(patch_user_ID: int, name: str = "", description: str = "", 
                cost: int = 0, attack: int = 0, health: int = 0,
                image_file: str = "", is_active: bool = False):
    try:
        conn = db.access()
        with conn:
            with conn.cursor() as cur:                
                cur.execute("""
                            INSERT INTO Cards
                            (name, description, cost, attack, health, image_file, is_active)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            RETURNING card_ID
                            """, (name, description, cost, attack, health, image_file, is_active))
                card_ID = cur.fetchone()[0]
                if not card_ID:
                    raise ValueError("잘못된 카드값이 반환되었습니다.")
                return card_ID
    except:
        raise

def update_card(before_id: int, card_after_update: Card, patch_user_ID: int):
    try:
        after_id = card_after_update.card_id
        if before_id <= 0:
            raise ValueError(f"카드 업데이트 오류: 대상 ID가 적절하지 않습니다: {before_id} ")
        if after_id <= 0:
            raise ValueError(f"카드 업데이트 오류: 대상 ID가 적절하지 않습니다: {after_id} ")
        if before_id != after_id:
            raise ValueError(f"카드 업데이트 오류: ID가 일치하지 않습니다. {before_id} != {after_id} ")
        name = card_after_update.name
        cost = card_after_update.cost
        attack = card_after_update.attack
        health = card_after_update.health
        image_file = card_after_update.image_file
        is_active = card_after_update.is_active
        ability_ids = [x.ability_id for x in card_after_update.abilities]
        conn = db.access()
        with conn:
            with conn.cursor() as cur:
                card_before_update = repo_card.get_card_info(conn, before_id)
                
                cur.execute("""
                            UPDATE Cards
                            SET name = %s,
                                cost = %s,
                                attack = %s,
                                health = %s,
                                image_file = %s,
                                is_active = %s
                            WHERE card_ID = %s
                            """, (name, cost, attack, health, image_file, is_active, before_id))
                
                cur.execute(
                    """
                    DELETE FROM Card_Abilities
                    WHERE card_id = %s
                    """,
                    (after_id,)
                )

                if ability_ids:
                    cur.executemany(
                        """
                        INSERT INTO Card_Abilities (card_id, ability_id)
                        VALUES (%s, %s)
                        """,
                        [(after_id, ability_id) for ability_id in ability_ids]
                    )

                cur.execute("""
                            INSERT INTO CardPatches
                            (card_ID, before, after, patch_user_ID)
                            VALUES (%s, %s, %s, %s)
                            """, (before_id, 
                                  json_card.card_to_json(card_before_update),
                                  json_card.card_to_json(card_after_update),
                                  patch_user_ID))
                
                if card_before_update.is_active and not card_after_update.is_active:
                    repo_deck.update_deck_incomplete(conn, before_id)        
    except Exception as e:
        raise e


def get_patch_list(card_id: int | None):
    print(card_id)
    try:
        with db.access() as conn:
            with conn.cursor() as cur:
                if card_id == 0:
                    raise ValueError("잘못된 card_ID입니다.")
                if card_id == None:
                    cur.execute("""
                            SELECT patch_ID, card_ID, before, after, changed_at, patch_user_ID 
                            FROM CardPatches
                            ORDER BY patch_ID DESC;
                            """)
                else:
                    cur.execute("""
                            SELECT patch_ID, card_ID, before, after, changed_at, patch_user_ID 
                            FROM CardPatches
                            WHERE card_ID = %s
                            ORDER BY patch_ID DESC;
                            """, (card_id,))
                rows = cur.fetchall()
                result = [Patch(
                    patch_ID=x[0],
                    card_ID=x[1],
                    before=json_card.json_to_card(x[2]),
                    after=json_card.json_to_card(x[3]),
                    diff_text=patch_builder.generate_diff_text(json_card.json_to_card(x[2]), json_card.json_to_card(x[3])),
                    change_at=x[4],
                    patch_user_ID=x[5]
                ) for x in rows]
                return result
                
    except Exception as e:
        raise e

            
        
            


