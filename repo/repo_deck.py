from models.models import Card, Ability
from psycopg2.extensions import connection

def update_deck_incomplete(conn: connection, card_ID: int):
    with conn.cursor() as cur:
        if card_ID is None:
            raise ValueError("Card ID가 없는데요?")

        cur.execute(
            """
            UPDATE decks
            SET is_complete = false,
                is_defense_deck = false
            WHERE deck_id IN (
                SELECT DISTINCT deck_id
                FROM deck_card_info
                WHERE card_id = %s
            )
            """,
            (card_ID,),
        )
        
