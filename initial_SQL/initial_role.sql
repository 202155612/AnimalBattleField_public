DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'guest') THEN
        CREATE ROLE guest;
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'player') THEN
        CREATE ROLE player;
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'developer') THEN
        CREATE ROLE developer;
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'administrator') THEN
        CREATE ROLE administrator;
    END IF;
END
$$;

GRANT guest TO player;
GRANT player TO developer;
GRANT player TO administrator;


GRANT USAGE ON SCHEMA public TO guest, player, developer, administrator;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO player, developer, administrator;

GRANT INSERT (user_ID, message)
ON Notifications
TO player;

GRANT INSERT (name, user_ID, is_complete, is_defense_deck)
ON Decks
TO player;

GRANT INSERT (deck_ID, slot, card_ID)
ON DeckCards
TO player;

GRANT INSERT (player1_ID, player2_ID, winner_player_side, last_patch_ID)
ON Matches
TO player;

GRANT INSERT (match_ID, state_num, turn)
ON MatchStates
TO player;

GRANT INSERT (
    match_id, action_num, turn,
    attack_side, attack_slot, target_slot,
    attacker_damage, target_damage,
    is_attacker_dead, is_target_dead,
    before_state_num, after_state_num
)
ON matchactions
TO player;


GRANT INSERT (match_ID, side, slot, card_ID, last_patch_ID)
ON MatchCards
TO player;

GRANT INSERT (match_id, state_num, side, slot, card_id, attack, health, is_dead)
ON matchstatecards
TO player;

GRANT UPDATE (is_read)
ON Notifications
TO player;

GRANT UPDATE (nickname)
ON Accounts
TO player;

GRANT UPDATE (card_ID)
ON DeckCards
TO player;

GRANT DELETE
ON Decks
TO player;

GRANT DELETE
ON DeckCards
TO player;

GRANT INSERT (name, description, cost, attack, health, image_file, is_active)
ON Cards
TO developer;

GRANT INSERT (card_ID, ability_ID)
ON Card_Abilities
TO developer;

GRANT INSERT (name, description, image_file)
ON Abilities
TO developer;

GRANT INSERT (card_ID, before, after, changed_at, patch_user_ID)
ON CardPatches
TO developer;

GRANT UPDATE (name, description, cost, attack, health, image_file, is_active)
ON Cards
TO developer;

GRANT UPDATE (name, description, image_file)
ON Abilities
TO developer;

GRANT UPDATE (is_complete, is_defense_deck)
ON Decks
TO developer;

GRANT DELETE
ON Cards
TO developer;

GRANT DELETE
ON Card_Abilities
TO developer;

GRANT DELETE
ON Abilities
TO developer;

GRANT UPDATE (nickname)
ON Accounts
TO administrator;

GRANT SELECT
ON DeckCards
To player;

GRANT UPDATE
ON decks
To player;

GRANT SELECT
ON decks
To player;

GRANT SELECT
ON Cards
TO developer;

GRANT SELECT
ON Abilities
TO developer;

GRANT SELECT
ON CardPatches
TO guest;

GRANT INSERT ON Matches TO player;
GRANT SELECT ON Matches TO player;

GRANT INSERT ON MatchStates TO player;
GRANT SELECT ON MatchStates TO player;

GRANT INSERT ON MatchActions TO player;
GRANT SELECT ON MatchActions TO player;

GRANT INSERT ON MatchCards TO player;
GRANT SELECT ON MatchCards TO player;

GRANT INSERT ON MatchStateCards TO player;
GRANT SELECT ON MatchStateCards TO player;

GRANT SELECT ON matches TO guest;