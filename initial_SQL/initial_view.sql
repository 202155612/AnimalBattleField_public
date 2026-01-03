CREATE VIEW card_info AS
SELECT
    c.card_id AS card_id,
    c.name AS name,
    c.cost AS cost,
    c.attack AS attack,
    c.health AS health,
    c.image_file AS image_file,
    c.is_active AS is_active,
    a.ability_id AS ability_id,
    a.name AS ability_name,
    a.description AS ability_description,
    a.image_file AS ability_image_file
FROM cards c
LEFT JOIN card_abilities ca ON c.card_id = ca.card_id
LEFT JOIN abilities a ON ca.ability_id = a.ability_id;

CREATE VIEW deck_info AS
SELECT
    d.deck_id AS deck_id,
    d.name AS deck_name,
    d.user_id AS user_id,
    d.is_complete AS is_complete,
    d.is_defense_deck AS is_defense_deck
FROM decks d;

CREATE VIEW deck_match AS
SELECT
    d.deck_id AS deck_id,
    d.name AS deck_name,
    d.user_id AS user_id,
    d.is_defense_deck AS is_defense_deck,
    a.nickname AS user_nickname
FROM decks d
JOIN Accounts a ON d.user_id = a.user_id;

CREATE VIEW deck_card_info AS
SELECT 
    dc.deck_id AS deck_id,
    dc.slot AS slot,
    c.card_id AS card_id,
    c.name AS card_name,
    c.cost AS cost,
    c.attack AS attack,
    c.health AS health,
    c.image_file AS image_file,
    c.is_active AS is_active,
    c.ability_id AS ability_id,
    c.ability_name AS ability_name,
    c.ability_description AS ability_description,
    c.ability_image_file AS ability_image_file
FROM deckcards dc
LEFT JOIN card_info c ON dc.card_id = c.card_id;

CREATE VIEW deck_complete AS
SELECT
    dc.deck_id AS deck_id,
    COUNT(dc.deck_id) AS card_num,
    SUM(c.cost) AS sum_cost,
    BOOL_AND(c.is_active) AS deck_is_active
FROM deckcards dc
JOIN cards c ON dc.card_id = c.card_id
GROUP BY deck_id;

CREATE VIEW total_matches AS
SELECT 
    COUNT(*) AS total_match_count
FROM Matches;

CREATE VIEW card_stats AS
WITH
attacker_dmg_as_attacker AS (
    SELECT
        mc.card_ID,
        SUM(ma.attacker_damage) AS attacker_damage_as_attacker
    FROM MatchCards mc
    JOIN MatchActions ma
      ON ma.match_ID    = mc.match_ID
     AND ma.attack_side = mc.side
     AND ma.attack_slot = mc.slot
    GROUP BY mc.card_ID
),

target_dmg_as_defender AS (
    SELECT
        mc.card_ID,
        SUM(ma.target_damage) AS target_damage_as_defender
    FROM MatchCards mc
    JOIN MatchActions ma
      ON ma.match_ID     = mc.match_ID
     AND ma.attack_side <> mc.side
     AND ma.target_slot  = mc.slot
    GROUP BY mc.card_ID
),

attacker_dmg_as_defender AS (
    SELECT
        mc.card_ID,
        SUM(ma.attacker_damage) AS attacker_damage_as_defender
    FROM MatchCards mc
    JOIN MatchActions ma
      ON ma.match_ID     = mc.match_ID
     AND ma.attack_side <> mc.side
     AND ma.target_slot  = mc.slot
    GROUP BY mc.card_ID
),

target_dmg_as_attacker AS (
    SELECT
        mc.card_ID,
        SUM(ma.target_damage) AS target_damage_as_attacker
    FROM MatchCards mc
    JOIN MatchActions ma
      ON ma.match_ID    = mc.match_ID
     AND ma.attack_side = mc.side
     AND ma.attack_slot = mc.slot
    GROUP BY mc.card_ID
),

kills_as_attacker AS (
    SELECT
        mc.card_ID,
        COUNT(ma.is_target_dead) AS kills_as_attacker
    FROM MatchCards mc
    JOIN MatchActions ma
      ON ma.match_ID    = mc.match_ID
     AND ma.attack_side = mc.side
     AND ma.attack_slot = mc.slot
    WHERE ma.is_target_dead = TRUE
    GROUP BY mc.card_ID
),

enemy_deaths_attacking_this AS (
    SELECT
        mc.card_ID,
        COUNT(ma.is_attacker_dead) AS enemy_deaths_attacking_this
    FROM MatchCards mc
    JOIN MatchActions ma
      ON ma.match_ID     = mc.match_ID
     AND ma.attack_side <> mc.side
     AND ma.target_slot  = mc.slot
    WHERE ma.is_attacker_dead = TRUE
    GROUP BY mc.card_ID
),

deaths_as_defender AS (
    SELECT
        mc.card_ID,
        COUNT(ma.is_target_dead) AS deaths_as_defender
    FROM MatchCards mc
    JOIN MatchActions ma
      ON ma.match_ID     = mc.match_ID
     AND ma.attack_side <> mc.side
     AND ma.target_slot  = mc.slot
    WHERE ma.is_target_dead = TRUE
    GROUP BY mc.card_ID
),

deaths_as_attacker AS (
    SELECT
        mc.card_ID,
        COUNT(ma.is_attacker_dead) AS deaths_as_attacker
    FROM MatchCards mc
    JOIN MatchActions ma
      ON ma.match_ID    = mc.match_ID
     AND ma.attack_side = mc.side
     AND ma.attack_slot = mc.slot
    WHERE ma.is_attacker_dead = TRUE
    GROUP BY mc.card_ID
),

matches_played AS (
    SELECT
        mc.card_ID,
        COUNT(DISTINCT mc.match_ID) AS matches_played
    FROM MatchCards mc
    GROUP BY mc.card_ID
),

matches_won AS (
    SELECT
        mc.card_ID,
        COUNT(DISTINCT m.match_ID) AS matches_won
    FROM MatchCards mc
    JOIN Matches m
      ON mc.match_ID = m.match_ID
     AND m.winner_player_side = mc.side
    GROUP BY mc.card_ID
),

matches_lost AS (
    SELECT
        mc.card_ID,
        COUNT(DISTINCT m.match_ID) AS matches_lost
    FROM MatchCards mc
    JOIN Matches m
      ON mc.match_ID = m.match_ID
     AND m.winner_player_side <> mc.side
     AND m.winner_player_side <> 0
    GROUP BY mc.card_ID
),

matches_drawn AS (
    SELECT
        mc.card_ID,
        COUNT(DISTINCT m.match_ID) AS matches_drawn
    FROM MatchCards mc
    JOIN Matches m
      ON mc.match_ID = m.match_ID
     AND m.winner_player_side = 0
    GROUP BY mc.card_ID
),

card_stat AS (
    SELECT
        c.card_ID AS card_ID,
        COALESCE(a1.attacker_damage_as_attacker, 0) AS attacker_damage_as_attacker,
        COALESCE(a2.target_damage_as_defender,   0) AS target_damage_as_defender,
        COALESCE(a3.attacker_damage_as_defender, 0) AS attacker_damage_as_defender,
        COALESCE(a4.target_damage_as_attacker,   0) AS target_damage_as_attacker,
        COALESCE(k1.kills_as_attacker,           0) AS kills_as_attacker,
        COALESCE(k2.enemy_deaths_attacking_this, 0) AS enemy_deaths_attacking_this,
        COALESCE(k3.deaths_as_defender,          0) AS deaths_as_defender,
        COALESCE(k4.deaths_as_attacker,          0) AS deaths_as_attacker,
        COALESCE(mp.matches_played,              0) AS matches_played,
        COALESCE(mw.matches_won,                 0) AS matches_won,
        COALESCE(ml.matches_lost,                0) AS matches_lost,
        COALESCE(md.matches_drawn,               0) AS matches_drawn
    FROM Cards c
    LEFT JOIN attacker_dmg_as_attacker      a1 ON c.card_ID = a1.card_ID
    LEFT JOIN target_dmg_as_defender        a2 ON c.card_ID = a2.card_ID
    LEFT JOIN attacker_dmg_as_defender      a3 ON c.card_ID = a3.card_ID
    LEFT JOIN target_dmg_as_attacker        a4 ON c.card_ID = a4.card_ID
    LEFT JOIN kills_as_attacker             k1 ON c.card_ID = k1.card_ID
    LEFT JOIN enemy_deaths_attacking_this   k2 ON c.card_ID = k2.card_ID
    LEFT JOIN deaths_as_defender            k3 ON c.card_ID = k3.card_ID
    LEFT JOIN deaths_as_attacker            k4 ON c.card_ID = k4.card_ID
    LEFT JOIN matches_played                mp ON c.card_ID = mp.card_ID
    LEFT JOIN matches_won                   mw ON c.card_ID = mw.card_ID
    LEFT JOIN matches_lost                  ml ON c.card_ID = ml.card_ID
    LEFT JOIN matches_drawn                 md ON c.card_ID = md.card_ID
)

SELECT
    cs.*,
    (cs.target_damage_as_attacker + cs.attacker_damage_as_defender) AS given_damage,
    (cs.attacker_damage_as_attacker + cs.target_damage_as_defender) AS taken_damage,
    (cs.kills_as_attacker + cs.enemy_deaths_attacking_this) AS total_kills,
    (cs.deaths_as_attacker + cs.deaths_as_defender) AS total_deaths
FROM card_stat cs
WHERE cs.card_ID <> 0
ORDER BY cs.card_ID;



CREATE VIEW login_data AS
SELECT
    user_ID,
    username,
    nickname
FROM Accounts;

CREATE VIEW account_data AS
SELECT
    username,
    nickname,
    created_at
FROM Accounts;



CREATE VIEW match_list AS
                SELECT
                    m.match_id AS match_id,
                    m.player1_id AS player1_ID,
                    m.player2_id AS player2_ID,
                    m.winner_player_side AS winner_player_side,
                    m.matched_at AS matched_at,
                    cp.patch_id AS match_last_patch_id,
                    cp.changed_at AS match_patch_changed_at,
                    acc1.nickname AS player1_nickname,
                    acc2.nickname AS player2_nickname,

                    mc.side AS card_side,
                    mc.slot AS card_slot,
                    mc.card_id AS card_id,

                    mcp.patch_id AS card_last_patch_id,
                    mcp.after AS card_last_patch_after
                FROM Matches m
                    JOIN CardPatches cp
                        ON m.last_patch_id = cp.patch_id 
                    JOIN Accounts acc1
                        ON m.player1_id = acc1.user_id
                    JOIN Accounts acc2
                        ON m.player2_id = acc2.user_id
                    JOIN MatchCards mc
                        ON m.match_id = mc.match_id
                    JOIN CardPatches mcp
                        ON mc.last_patch_id = mcp.patch_id;

CREATE VIEW match_card_patch AS
                SELECT
                    mc.match_id AS match_id,
                    mc.side AS card_side,
                    mc.slot AS card_slot,
                    mc.card_id AS base_card_id,
                    cp.patch_id AS card_last_patch_id,
                    cp.after AS card_patch_after
                FROM MatchCards mc
                    JOIN CardPatches cp
                        ON mc.last_patch_id = cp.patch_id;


CREATE VIEW match_turn AS
SELECT
                    ma.match_id AS match_id,
                    ma.action_id AS action_id,
                    ma.action_num AS action_num,
                    ma.turn AS turn,
                    ma.attack_side AS attack_side,
                    ma.attack_slot AS attack_slot,
                    ma.target_slot AS target_slot,
                    ma.attacker_damage AS attacker_damage,
                    ma.target_damage AS target_damage,
                    ma.is_attacker_dead AS is_attacker_dead,
                    ma.is_target_dead AS is_target_dead,
                    ms_before.state_id AS before_state_id,
                    ms_before.state_num AS before_state_num,
                    ms_before.turn AS before_turn,
                    ms_after.state_id AS after_state_id,
                    ms_after.state_num AS after_state_num,
                    ms_after.turn AS after_turn,
                    msc_before.side AS before_side,
                    msc_before.slot AS before_slot,
                    msc_before.attack AS before_attack,
                    msc_before.health AS before_health,
                    msc_before.is_dead AS before_is_dead,
                    msc_after.side AS after_side,
                    msc_after.slot AS after_slot,
                    msc_after.attack AS after_attack,
                    msc_after.health AS after_health,
                    msc_after.is_dead AS after_is_dead
                FROM MatchActions ma
                    JOIN MatchStates ms_before
                        ON ma.match_id = ms_before.match_id
                    AND ma.before_state_num = ms_before.state_num
                    JOIN MatchStates ms_after
                        ON ma.match_id = ms_after.match_id
                    AND ma.after_state_num = ms_after.state_num
                    JOIN MatchStateCards msc_before
                        ON ms_before.match_id = msc_before.match_id
                    AND ms_before.state_num = msc_before.state_num
                    JOIN MatchStateCards msc_after
                        ON ms_after.match_id = msc_after.match_id
                    AND ms_after.state_num = msc_after.state_num
                    AND msc_before.side = msc_after.side
                    AND msc_before.slot = msc_after.slot;
