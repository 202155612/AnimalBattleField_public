import psycopg2
import database.database as db
from collections import defaultdict
from utils import json_card
import json
from models.models import (
    Replay,
    ReplayAction,
    ReplayCard,
    ReplayState,
    ReplayStateCard,
    Card,
    CardWithLastPatch,
)


def get_replay(match_id: int) -> Replay:
    if not match_id:
        raise ValueError("리플레이 ID가 없습니다.")

    conn = db.access()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    match_id,
                    player1_id,
                    player2_id,
                    winner_player_side,
                    matched_at,
                    match_last_patch_id,
                    match_patch_changed_at,
                    player1_nickname,
                    player2_nickname
                FROM match_list
                WHERE match_id = %s
                LIMIT 1
                """,
                (match_id,),
            )
            row = cur.fetchone()

            if not row:
                raise ValueError(f"리플레이 {match_id}가 없습니다.")

            (
                row_match_id,
                row_player1_id,
                row_player2_id,
                row_winner_player_side,
                row_matched_at,
                row_match_last_patch_id,
                row_match_patch_changed_at,
                row_player1_nickname,
                row_player2_nickname,
            ) = row

            replay = Replay(
                replay_id=row_match_id,
                player1_id=row_player1_id,
                player2_id=row_player2_id,
                player1_nickname=row_player1_nickname,
                player2_nickname=row_player2_nickname,
                winner_player_side=row_winner_player_side,
                matched_at=row_matched_at,
                last_patch_id=row_match_last_patch_id,
            )

            base_cards = {}
            card_with_patches = {}

            cur.execute(
                """
                SELECT
                    match_id,
                    card_side,
                    card_slot,
                    base_card_id,
                    card_last_patch_id,
                    card_patch_after
                FROM match_card_patch
                WHERE match_id = %s
                ORDER BY card_side, card_slot
                """,
                (match_id,),
            )
            card_rows = cur.fetchall()

            if not card_rows:
                raise ValueError(f"매치 {match_id}에 카드 정보가 없습니다.")

            for (
                _,
                card_side,
                card_slot,
                base_card_id,
                card_last_patch_id,
                card_patch_after,
            ) in card_rows:

                key = (card_side, card_slot)
                card_data = card_patch_after
                if isinstance(card_data, str):
                    card_data = json.loads(card_data)

                base_card = json_card.json_to_card(card_data)
                base_cards[key] = base_card

                cwl = CardWithLastPatch(base_card, card_last_patch_id)
                card_with_patches[key] = cwl

                rc = ReplayCard(card_side, card_slot, cwl)

                if card_side == 1:
                    replay.player1_cards.append(rc)
                else:
                    replay.player2_cards.append(rc)

            replay.player1_cards.sort(key=lambda c: c.slot)
            replay.player2_cards.sort(key=lambda c: c.slot)

            cur.execute(
                """
                SELECT
                    match_id,
                    action_id,
                    action_num,
                    turn,
                    attack_side,
                    attack_slot,
                    target_slot,
                    attacker_damage,
                    target_damage,
                    is_attacker_dead,
                    is_target_dead,
                    before_state_id,
                    before_state_num,
                    before_turn,
                    after_state_id,
                    after_state_num,
                    after_turn,
                    before_side,
                    before_slot,
                    before_attack,
                    before_health,
                    before_is_dead,
                    after_side,
                    after_slot,
                    after_attack,
                    after_health,
                    after_is_dead
                FROM match_turn
                WHERE match_id = %s
                ORDER BY action_num, before_state_num, before_side, before_slot
                """,
                (match_id,),
            )
            action_rows = cur.fetchall()

            states = {}
            state_cards_seen = defaultdict(set)
            actions = {}

            if not action_rows:
                replay.actions = []
                return replay

            for row in action_rows:
                (
                    match_id,
                    action_id,
                    action_num,
                    action_turn,
                    attack_side,
                    attack_slot,
                    target_slot,
                    attacker_damage,
                    target_damage,
                    is_attacker_dead,
                    is_target_dead,
                    before_state_id,
                    before_state_num,
                    before_turn,
                    after_state_id,
                    after_state_num,
                    after_turn,
                    before_side,
                    before_slot,
                    before_attack,
                    before_health,
                    before_is_dead,
                    after_side,
                    after_slot,
                    after_attack,
                    after_health,
                    after_is_dead,
                ) = row

                if before_state_num not in states:
                    states[before_state_num] = ReplayState(
                        state_num=before_state_num,
                        turn=before_turn,
                    )

                if after_state_num not in states:
                    states[after_state_num] = ReplayState(
                        state_num=after_state_num,
                        turn=after_turn,
                    )

                before_state = states[before_state_num]
                after_state = states[after_state_num]

                key = (before_side, before_slot)
                base_card = base_cards.get(key)

                if base_card is None:
                    raise RuntimeError(
                        f"카드 정보가 없습니다. side={before_side}, slot={before_slot}"
                    )

                if key not in state_cards_seen[before_state_num]:
                    state_cards_seen[before_state_num].add(key)
                    target = (
                        before_state.player1_cards
                        if before_side == 1
                        else before_state.player2_cards
                    )
                    target.append(
                        ReplayStateCard(
                            side=before_side,
                            slot=before_slot,
                            card=base_card,
                            attack=before_attack,
                            health=before_health,
                            is_dead=before_is_dead,
                        )
                    )

                if key not in state_cards_seen[after_state_num]:
                    state_cards_seen[after_state_num].add(key)
                    target = (
                        after_state.player1_cards
                        if after_side == 1
                        else after_state.player2_cards
                    )
                    target.append(
                        ReplayStateCard(
                            side=after_side,
                            slot=after_slot,
                            card=base_card,
                            attack=after_attack,
                            health=after_health,
                            is_dead=after_is_dead,
                        )
                    )

                action = actions.get(action_num)
                if action is None:
                    actions[action_num] = ReplayAction(
                        action_num=action_num,
                        turn=action_turn,
                        attack_side=attack_side,
                        attack_slot=attack_slot,
                        target_slot=target_slot,
                        attacker_damage=attacker_damage,
                        target_damage=target_damage,
                        is_attacker_dead=is_attacker_dead,
                        is_target_dead=is_target_dead,
                        before_state=before_state,
                        after_state=after_state,
                    )

            replay.actions = [actions[n] for n in sorted(actions.keys())]

    return replay


def get_replay_list(user_id: int | None = None, patch_id: int | None = None):
    conn = db.access()
    with conn:
        with conn.cursor() as cur:
            query = """
                SELECT
                    match_id,
                    player1_id,
                    player2_id,
                    winner_player_side,
                    matched_at,
                    match_last_patch_id,
                    match_patch_changed_at,
                    player1_nickname,
                    player2_nickname,
                    card_side,
                    card_slot,
                    card_id,
                    card_last_patch_id,
                    card_last_patch_after
                FROM match_list
            """
            vars = []

            if user_id is not None:
                query += " WHERE (player1_id = %s OR player2_id = %s)"
                vars += [user_id, user_id]
                if patch_id is not None:
                    query += " AND match_last_patch_id >= %s"
                    vars.append(patch_id)
            else:
                if patch_id is not None:
                    query += " WHERE match_last_patch_id >= %s"
                    vars.append(patch_id)

            query += " ORDER BY match_id DESC, card_side ASC, card_slot ASC"

            cur.execute(query, vars)
            rows = cur.fetchall()

            replays = {}

            for (
                match_id,
                player1_id,
                player2_id,
                winner_player_side,
                matched_at,
                match_last_patch_id,
                match_patch_changed_at,
                player1_nickname,
                player2_nickname,
                card_side,
                card_slot,
                card_id,
                card_last_patch_id,
                card_last_patch_after,
            ) in rows:

                if match_id not in replays:
                    replays[match_id] = Replay(
                        replay_id=match_id,
                        player1_id=player1_id,
                        player2_id=player2_id,
                        player1_nickname=player1_nickname,
                        player2_nickname=player2_nickname,
                        winner_player_side=winner_player_side,
                        last_patch_id=match_last_patch_id,
                        matched_at=matched_at,
                        player1_cards=[],
                        player2_cards=[],
                        actions=[],
                    )

                card_data = card_last_patch_after
                if isinstance(card_data, str):
                    card_data = json.loads(card_data)

                card_obj = json_card.json_to_card(card_data)
                rc = ReplayCard(
                    card_side,
                    card_slot,
                    CardWithLastPatch(card_obj, card_last_patch_id),
                )

                if card_side == 1:
                    replays[match_id].player1_cards.append(rc)
                else:
                    replays[match_id].player2_cards.append(rc)

            return sorted(replays.values(), key=lambda x: -x.replay_id)
