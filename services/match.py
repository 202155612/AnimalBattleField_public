import psycopg2
import database.database as db
from flask import session
import traceback
import random
from repo import repo_card
from models.models import DeckAccount, MatchResult


def get_defense_deck_id(player_id):
    if not player_id:
        raise ValueError("플레이어 ID가 없습니다.")
    try:
        conn = db.access()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT deck_id, deck_name, user_id, user_nickname
                    FROM deck_match
                    WHERE user_id <> %s
                        AND is_defense_deck = True;
                    """, (player_id, )
                )
                possible_decks = cur.fetchall()
                if not possible_decks:
                    raise ValueError("상대할 만한 덱이 없습니다.")
                enemy_deck = random.choice(possible_decks)
                deck_id, deck_name, user_id, user_nickname = enemy_deck

                cards = repo_card.card_with_last_patch_builders(conn, deck_id)
                if None in cards:
                    raise ValueError("빈 카드가 있습니다.")
                return DeckAccount(
                    deck_id = deck_id,
                    deck_name = deck_name,
                    user_id = user_id,
                    user_nickname = user_nickname,
                    cards = cards
                )
    except Exception as e:
        raise(e)
    
def get_last_patch_id():
    try:
        conn = db.access()
        with conn:
            last_patch = repo_card.get_last_patch(conn, None)
            if last_patch == None:
                raise ValueError(f"마지막 패치 ID를 가져오지 못했습니다.")
            return last_patch.patch_ID
    except:
        raise


def insert_result(player1: DeckAccount, player2: DeckAccount, result: MatchResult) -> int:
    if result is None:
        raise ValueError("매칭 결과가 insert될 수 없습니다.")

    conn = db.access()

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO Matches
                        (player1_ID, player2_ID, winner_player_side, last_patch_ID, matched_at)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING match_ID
                    """,
                    (
                        player1.user_id,
                        player2.user_id,
                        result.result,
                        result.last_patch_id,
                        result.matched_at,
                    ),
                )
                match_id = cur.fetchone()[0]

                for state in sorted(result.match_states, key=lambda s: s.state_num):
                    cur.execute(
                        """
                        INSERT INTO MatchStates
                            (match_ID, state_num, turn)
                        VALUES (%s, %s, %s)
                        """,
                        (match_id, state.state_num, state.turn),
                    )

                for action in sorted(result.match_actions, key=lambda a: a.action_num):
                    cur.execute(
                        """
                        INSERT INTO MatchActions
                            (match_ID,
                             action_num, turn,
                             attack_side, attack_slot, target_slot,
                             attacker_damage, target_damage,
                             is_attacker_dead, is_target_dead,
                             before_state_num, after_state_num)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            match_id,
                            action.action_num,
                            action.turn,
                            action.attack_side,
                            action.attack_slot,
                            action.target_slot,
                            action.attacker_damage,
                            action.target_damage,
                            action.is_attacker_dead,
                            action.is_target_dead,
                            action.before_state_num,
                            action.after_state_num,
                        ),
                    )

                for c in result.match_state_cards:
                    cur.execute(
                        """
                        INSERT INTO MatchStateCards
                            (match_ID, state_num, side, slot, card_ID,
                             attack, health, is_dead)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            match_id,
                            c.state_num,
                            c.side,
                            c.slot,
                            c.card_ID,
                            c.attack,
                            c.health,
                            c.is_dead,
                        ),
                    )

                p1_patch_map = {c.card.card_id: c.last_patch_id for c in player1.cards}
                p2_patch_map = {c.card.card_id: c.last_patch_id for c in player2.cards}

                position_to_card = {}
                for c in sorted(result.match_state_cards, key=lambda x: x.state_num):
                    key = (c.side, c.slot)
                    if key not in position_to_card:
                        position_to_card[key] = c.card_ID

                for (side, slot), card_id in position_to_card.items():
                    if side == 1:
                        patch_map = p1_patch_map
                    elif side == 2:
                        patch_map = p2_patch_map
                    else:
                        raise ValueError(f"알 수 없는 side 값: {side}")

                    if card_id not in patch_map:
                        raise ValueError(
                            f"side={side}, slot={slot}의 card_id={card_id} 에 대한 패치 정보를 찾을 수 없습니다."
                        )

                    last_patch_id = patch_map[card_id]

                    cur.execute(
                        """
                        INSERT INTO MatchCards
                            (match_ID, side, slot, card_ID, last_patch_ID)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (match_id, side, slot, card_id, last_patch_id),
                    )

                return match_id
    except:
        raise
    finally:
        if conn != None:
            conn.close()
