import psycopg2
import database.database as db
from flask import session
import traceback
from repo import repo_card 
from models.models import Deck, SimpleCard, SimpleDeck, DeckAccount
from typing import Optional

MAX_COST = 20

def get_deck_list(user_id, only_complete=None):
    conn = None
    if not user_id:
        return []
    try:
        conn = db.access()
        with conn:
            with conn.cursor() as cur:
                query = """
                    SELECT 
                        di.deck_id,
                        di.deck_name,
                        di.is_complete,
                        di.is_defense_deck,
                        dci.slot,
                        dci.card_id,
                        dci.image_file,
                        dci.is_active
                    FROM deck_info di
                    LEFT JOIN deck_card_info dci ON di.deck_id = dci.deck_id
                    WHERE di.user_id = %s
                """

                params = [user_id]

                if only_complete is True:
                    query += " AND di.is_complete = True"
                elif only_complete is False:
                    query += " AND di.is_complete = False"

                cur.execute(query + ";", params)
                rows = cur.fetchall()

                decks: dict[int, Deck] = {}
                for row in rows:
                    deck_id, deck_name, is_complete, is_defense_deck, slot, card_id, image_file, is_active = row

                    if deck_id not in decks:
                        decks[deck_id] = SimpleDeck(
                            deck_id,
                            deck_name,
                            is_complete,
                            is_defense_deck,
                            [None, None, None, None]
                        )
                    if card_id is not None:
                        decks[deck_id].cards[slot] = SimpleCard(card_id, image_file, is_active)

                return list(decks.values())

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        raise e


def get_deck_user_id(deck_ID):
    try:
        conn = db.access()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT user_ID
                    FROM deck_info
                    WHERE deck_ID = %s    
                """, (deck_ID,))
                row = cur.fetchone()
                if row is None:
                    return None
                return row[0]

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        raise e
    
def create_deck(user_ID:int, deck_name: str):
    print(session["user_ID"])
    print(session["username"])
    try:
        conn = db.access()
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT current_user, session_user, current_schema()")
                print("DB user/schema:", cur.fetchone())
                cur.execute("""
                    INSERT INTO Decks
                        (name, user_ID, is_complete, is_defense_deck)
                        VALUES (%s, %s, False, False)
                    RETURNING deck_ID;
                """, (deck_name, user_ID,))
                deck_ID = cur.fetchone()[0]
                return deck_ID

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        raise e
    
def get_deck_info(deck_ID: int):
    try:
        conn = db.access()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT deck_name, is_complete, is_defense_deck
                    FROM deck_info
                    WHERE deck_id = %s;
                """, (deck_ID,))
                deck = cur.fetchone()
                if not deck:
                    print(f"Database error: There is no deck {deck_ID}")
                    return None
                deck_name, is_complete, is_defense_deck = deck

                cards = repo_card.card_slot_builders(conn, deck_ID)
                return Deck(
                    deck_ID,
                    deck_name,
                    is_complete,
                    is_defense_deck,
                    cards
                )
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        raise e

def get_deck_info_with_last_patches(deck_ID: int) -> DeckAccount:
    try:
        conn = db.access()
        with conn:
            with conn.cursor() as cur:                
                cur.execute("""
                    SELECT deck_id, deck_name, user_id, user_nickname
                    FROM deck_match
                    WHERE deck_id = %s
                    """, (deck_ID, )
                )
                deck = cur.fetchone()
                if not deck:
                    print(f"Database error: There is no deck {deck_ID}")
                    return None
                deck_id, deck_name, user_id, user_nickname = deck
                cards = repo_card.card_with_last_patch_builders(conn, deck_ID)
                print(f"user_ID : {user_id}")
                return DeckAccount(
                    deck_id = deck_id,
                    deck_name = deck_name,
                    user_id = user_id,
                    user_nickname = user_nickname,
                    cards = cards
                )
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        raise e


def update_card(deck_ID: int, card_IDs: list[Optional[int]]):
    if len(card_IDs) != 4:
        raise ValueError("카드가 네 장이 아닌데요?")

    try:
        conn = db.access()
        with conn:
            with conn.cursor() as cur:
                for slot, card_ID in enumerate(card_IDs):
                    if card_ID is None:
                        cur.execute("""
                            DELETE FROM deckcards
                            WHERE deck_id = %s AND slot = %s;
                        """, (deck_ID, slot))
                    else:
                        cur.execute("""
                            INSERT INTO deckcards (deck_id, slot, card_id)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (deck_id, slot)
                            DO UPDATE SET card_id = EXCLUDED.card_id;
                        """, (deck_ID, slot, card_ID))

                cur.execute("""
                    UPDATE decks
                    SET is_complete = %s,
                        is_defense_deck = %s
                    WHERE deck_id = %s;
                """, (False, False, deck_ID))

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        raise e
    
def update_deck_name(deck_id, new_deck_name):
    try:
        conn = db.access()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE decks
                    SET name = %s
                    WHERE
                        deck_id = %s
                            """, (new_deck_name, deck_id)
                )
                
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        raise e
    
    
    
def update_deck_status(deck_id, deck_complete):
    if deck_complete == "not_complete":
        is_complete = False
        is_defense_deck = False
    elif deck_complete == "complete":
        is_complete = True
        is_defense_deck = False
    elif deck_complete == "defense_deck":
        is_complete = True
        is_defense_deck = True
    else:
        raise ValueError("complete 값이 없습니다.")
    try:
        conn = db.access()
        with conn:
            with conn.cursor() as cur:
                if is_complete:
                    cur.execute("""
                        SELECT card_num, sum_cost, deck_is_active
                        FROM deck_complete
                        WHERE deck_id = %s
                    """, (deck_id,))
                    row = cur.fetchone()
                    if row is None:
                        raise ValueError("덱이 완성 조건을 만족하지 않습니다.")
                    card_num, sum_cost, deck_is_active = row
                    

                cur.execute("""
                    UPDATE decks
                    SET is_complete = %s,
                        is_defense_deck = %s
                    WHERE
                        deck_id = %s
                            """, (is_complete, is_defense_deck, deck_id)
                )            
    except psycopg2.Error as e:
        traceback.print_exc()
        print(f"Database error: {e}")
        raise e
    


