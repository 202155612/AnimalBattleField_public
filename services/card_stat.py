import psycopg2
import database.database as db
from collections import defaultdict
from utils import json_card
import json
from repo import repo_card
from models.models import CardStats, Card

def get_card_stat_list(
    search_card_id: int = None, search_name: str = None,
    cost: int = None, min_cost: int = None, max_cost: int = None,
    attack:int = None, min_attack: int = None, max_attack: int = None,
    health: int = None, min_health: int = None, max_health: int = None,
    is_active: bool = None, no_zero_id: bool = True
) -> list[CardStats]:
    conn = db.access()
    with conn:
        cards = repo_card.card_list_builders(
            conn, search_card_id, search_name,
            cost, min_cost, max_cost,
            attack, min_attack, max_attack,
            health, min_health, max_health,
            is_active, no_zero_id, lambda x:x.card_id
        )

        card_ids = tuple(x.card_id for x in cards)

        if not card_ids:
            return []

        card_lookup = {c.card_id: c for c in cards}

        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    card_ID,
                    attacker_damage_as_attacker,
                    target_damage_as_defender,
                    attacker_damage_as_defender,
                    target_damage_as_attacker,
                    kills_as_attacker,
                    enemy_deaths_attacking_this,
                    deaths_as_defender,
                    deaths_as_attacker,
                    matches_played,
                    matches_won,
                    matches_lost,
                    matches_drawn,
                    given_damage,
                    taken_damage,
                    total_deaths,
                    total_kills
                FROM card_stats 
                WHERE card_ID IN %s
                ORDER BY card_ID;
                """,
                (card_ids,)
            )

            rows = cur.fetchall()

        stats: list[CardStats] = []

        for row in rows:
            (
                card_id,
                attacker_damage_as_attacker,
                target_damage_as_defender,
                attacker_damage_as_defender,
                target_damage_as_attacker,
                kills_as_attacker,
                enemy_deaths_attacking_this,
                deaths_as_defender,
                deaths_as_attacker,
                matches_played,
                matches_won,
                matches_lost,
                matches_drawn,
                given_damage,
                taken_damage,
                total_deaths,
                total_kills
            ) = row

            played = matches_played or 0
            wins = matches_won or 0
            draws = matches_drawn or 0
            losses = matches_lost or 0
            given = given_damage or 0
            taken = taken_damage or 0
            deaths = total_deaths or 0
            kills = total_kills or 0

            if played > 0:
                win_rate = wins / played
                draw_rate = draws / played
                lose_rate = losses / played
                avg_given_damage = given / played
                avg_taken_damage = taken / played
                avg_kills = kills / played
                avg_deaths = deaths / played
            else:
                win_rate = 0.0
                draw_rate = 0.0
                lose_rate = 0.0
                avg_given_damage = 0.0
                avg_taken_damage = 0.0
                avg_kills = 0.0
                avg_deaths = 0.0

            if deaths > 0:
                kd_ratio = kills / deaths
            else:
                kd_ratio = float(kills)

            card = card_lookup.get(card_id)
            stats.append(
                CardStats(
                    card=card,
                    card_name=card.name,
                    card_image=card.image_file,
                    card_id=card.card_id,
                    attacker_damage_as_attacker=attacker_damage_as_attacker,
                    target_damage_as_defender=target_damage_as_defender,
                    attacker_damage_as_defender=attacker_damage_as_defender,
                    target_damage_as_attacker=target_damage_as_attacker,
                    kills_as_attacker=kills_as_attacker,
                    enemy_deaths_attacking_this=enemy_deaths_attacking_this,
                    deaths_as_defender=deaths_as_defender,
                    deaths_as_attacker=deaths_as_attacker,
                    matches_played=matches_played,
                    matches_won=matches_won,
                    matches_lost=matches_lost,
                    matches_drawn=matches_drawn,
                    given_damage=given_damage,
                    taken_damage=taken_damage,
                    total_kills=total_kills,
                    total_deaths=total_deaths,
                    win_rate=win_rate,
                    draw_rate=draw_rate,
                    lose_rate=lose_rate,
                    avg_given_damage=avg_given_damage,
                    avg_taken_damage=avg_taken_damage,
                    avg_kills=avg_kills,
                    avg_deaths=avg_deaths,
                    kd_ratio=kd_ratio
                )
            )

        return stats
