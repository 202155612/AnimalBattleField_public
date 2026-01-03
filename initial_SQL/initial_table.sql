DROP SCHEMA public CASCADE; 
CREATE SCHEMA public;

CREATE TABLE Accounts (
    user_ID         SERIAL PRIMARY KEY,
    username        VARCHAR(50) NOT NULL UNIQUE,
    nickname        VARCHAR(50) NOT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Notifications (
    notification_ID SERIAL PRIMARY KEY,
    user_ID         INTEGER NOT NULL,
    message         VARCHAR(255) NOT NULL,
    is_read         BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_ID) REFERENCES Accounts(user_ID)
);

CREATE TABLE Cards (
    card_ID         SERIAL PRIMARY KEY,
    name            VARCHAR(50) NOT NULL,
    description     VARCHAR(255) NOT NULL,
    cost            INTEGER NOT NULL,
    attack          INTEGER NOT NULL,
    health          INTEGER NOT NULL CHECK (health >= 0),
    image_file      VARCHAR(255),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE    
);

CREATE TABLE Abilities (
    ability_ID      SERIAL PRIMARY KEY,
    name            VARCHAR(50) NOT NULL,
    description     VARCHAR(255) NOT NULL,
    image_file      VARCHAR(255) NOT NULL
);

CREATE TABLE Card_Abilities (
    card_ID         INTEGER REFERENCES Cards(card_ID),
    ability_ID      INTEGER REFERENCES Abilities(ability_ID),
    PRIMARY KEY (card_ID, ability_ID)
);

CREATE TABLE Decks (
    deck_ID         SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    user_ID         INTEGER NOT NULL,
    is_complete     BOOLEAN NOT NULL,
    is_defense_deck BOOLEAN NOT NULL,
    FOREIGN KEY (user_ID) REFERENCES Accounts(user_ID)
);

CREATE TABLE DeckCards (
    deck_ID         INTEGER NOT NULL,
    slot            INTEGER NOT NULL CHECK (slot >= 0 AND slot < 4),
    card_ID         INTEGER,
    PRIMARY KEY (deck_ID, slot),
    FOREIGN KEY (deck_ID) REFERENCES Decks(deck_ID),
    FOREIGN KEY (card_ID) REFERENCES Cards(card_ID)
);

CREATE TABLE CardPatches (
    patch_ID        SERIAL PRIMARY KEY,
    card_ID         INTEGER NOT NULL,
    before          JSONB NOT NULL,
    after           JSONB NOT NULL,
    changed_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    patch_user_ID   INTEGER NOT NULL,
    FOREIGN KEY (card_ID) REFERENCES Cards(card_ID) ON DELETE CASCADE,
    FOREIGN KEY (patch_user_ID) REFERENCES Accounts(user_ID)
);

CREATE TABLE Matches (
    match_ID            SERIAL PRIMARY KEY,
    player1_ID          INTEGER NOT NULL,
    player2_ID          INTEGER NOT NULL,
    winner_player_side  INTEGER NOT NULL CHECK (winner_player_side IN (0, 1, 2)),
    last_patch_ID       INTEGER NOT NULL,
    matched_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player1_ID) REFERENCES Accounts(user_ID) ON DELETE RESTRICT,
    FOREIGN KEY (player2_ID) REFERENCES Accounts(user_ID) ON DELETE RESTRICT,
    FOREIGN KEY (last_patch_ID) REFERENCES CardPatches(patch_ID) ON DELETE RESTRICT
);

CREATE TABLE MatchStates (
    state_ID        SERIAL PRIMARY KEY,
    match_ID        INTEGER NOT NULL,
    state_num       INTEGER NOT NULL CHECK (state_num >= 0),
    turn            INTEGER NOT NULL,
    FOREIGN KEY (match_ID) REFERENCES Matches(match_ID) ON DELETE CASCADE,
    UNIQUE (match_ID, state_num),
    UNIQUE (match_ID, state_ID)
);

CREATE TABLE MatchActions (
    action_ID           SERIAL PRIMARY KEY,
    match_ID            INTEGER NOT NULL,
    action_num          INTEGER NOT NULL CHECK (action_num >= 0),
    turn                INTEGER NOT NULL,
    attack_side         INTEGER NOT NULL CHECK (attack_side IN (1, 2)),
    attack_slot         INTEGER NOT NULL CHECK (attack_slot >= 0),
    target_slot         INTEGER NOT NULL CHECK (target_slot >= 0),
    attacker_damage     INTEGER NOT NULL,
    target_damage       INTEGER NOT NULL,
    is_attacker_dead    BOOLEAN NOT NULL,
    is_target_dead      BOOLEAN NOT NULL,
    before_state_num    INTEGER NOT NULL,
    after_state_num     INTEGER NOT NULL,
    FOREIGN KEY (match_ID, before_state_num) REFERENCES MatchStates(match_ID, state_num) ON DELETE CASCADE,
    FOREIGN KEY (match_ID, after_state_num) REFERENCES MatchStates(match_ID, state_num) ON DELETE CASCADE,
    UNIQUE (match_ID, action_num)
);


CREATE TABLE MatchCards (
    match_ID        INTEGER NOT NULL,
    side            INTEGER NOT NULL CHECK (side IN (1, 2)),
    slot            INTEGER NOT NULL CHECK (slot >= 0),
    card_ID         INTEGER NOT NULL DEFAULT 0,
    last_patch_ID   INTEGER NOT NULL,
    PRIMARY KEY (match_ID, side, slot),
    FOREIGN KEY (match_ID) REFERENCES Matches(match_ID) ON DELETE CASCADE,
    FOREIGN KEY (card_ID) REFERENCES Cards(card_ID) ON DELETE CASCADE,
    FOREIGN KEY (last_patch_ID) REFERENCES CardPatches(patch_ID) ON DELETE RESTRICT
);

CREATE TABLE MatchStateCards (
    match_ID        INTEGER NOT NULL,
    state_num       INTEGER NOT NULL,
    side            INTEGER NOT NULL CHECK (side IN (1, 2)),
    slot            INTEGER NOT NULL CHECK (slot >= 0),
    card_ID         INTEGER NOT NULL DEFAULT 0,
    attack          INTEGER NOT NULL,
    health          INTEGER NOT NULL,
    is_dead         BOOLEAN NOT NULL,
    PRIMARY KEY (match_ID, state_num, side, slot),
    FOREIGN KEY (match_ID, state_num) REFERENCES MatchStates(match_ID, state_num) ON DELETE CASCADE,
    FOREIGN KEY (card_ID) REFERENCES Cards(card_ID) ON DELETE SET DEFAULT
);



CREATE INDEX ON Cards(cost);
CREATE INDEX ON Cards(attack);
CREATE INDEX ON Cards(health);
CREATE INDEX ON Cards(is_active);

CREATE INDEX ON Card_Abilities(card_id);

CREATE INDEX ON Decks(user_id, is_complete);
CREATE INDEX ON Decks(is_defense_deck);

CREATE INDEX ON Deckcards(card_id);

CREATE UNIQUE INDEX ON Accounts(username);

CREATE INDEX ON CardPatches(card_id, patch_id);

CREATE INDEX ON Matches(player1_id, match_id);
CREATE INDEX ON Matches(player2_id, match_id);
CREATE INDEX ON Matches(last_patch_id, match_id);

CREATE INDEX ON MatchCards(match_id, side, slot);
CREATE INDEX ON MatchCards(card_id, match_id);

CREATE INDEX ON MatchActions(match_id, action_num);
CREATE INDEX ON MatchActions(match_id, attack_side, attack_slot);
CREATE INDEX ON MatchActions(match_id, target_slot);

CREATE INDEX ON MatchStates(match_id, state_num);

CREATE INDEX ON MatchStateCards(match_id, state_num, side, slot);

