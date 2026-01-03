from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Account:
    username: str
    nickname: str
    created_at: datetime
    role: list[str] = field(default_factory=list)

@dataclass
class Ability:
    ability_id: int
    name: str
    desc: str
    image_file: str

@dataclass
class Card:
    card_id: int
    name: str
    cost: int
    attack: int
    health: int
    image_file: str
    is_active: bool
    abilities: list[Ability] = field(default_factory=list)

@dataclass
class CardWithLastPatch:
    card: Card
    last_patch_id: int

@dataclass
class SimpleCard:
    card_id: int
    image_file: str
    is_active: bool

@dataclass
class Deck:
    deck_id: int
    name: str
    is_complete: bool
    is_defense_deck: bool
    cards: list[Card] = field(default_factory=list)


@dataclass
class SimpleDeck:
    deck_id: int
    name: str
    is_complete: bool
    is_defense_deck: bool
    cards: list[SimpleCard] = field(default_factory=list)

@dataclass
class DeckAccount:  
    deck_id: int
    deck_name: str
    user_id: int
    user_nickname: str
    cards: list[CardWithLastPatch] = field(default_factory=list)

@dataclass
class MatchState:
    state_num: int
    turn: int

@dataclass
class MatchStateCard:
    state_num: int
    side: int
    slot: int
    card_ID: int
    attack: int
    health: int
    is_dead: bool

@dataclass
class MatchAction:
    action_num: int
    turn: int
    attack_side: int
    attack_slot: int
    target_slot: int
    attacker_damage: int
    target_damage: int
    is_attacker_dead: bool
    is_target_dead: bool
    before_state_num: int
    after_state_num: int

@dataclass
class MatchResult:
    result: int
    matched_at: datetime
    last_patch_id: int
    match_states: list[MatchState] = field(default_factory=list)
    match_state_cards: list[MatchStateCard] = field(default_factory=list)
    match_actions: list[MatchAction] = field(default_factory=list)

@dataclass
class Patch:
    patch_ID: int
    card_ID: int
    before: Card
    after: Card
    diff_text: str
    change_at: datetime
    patch_user_ID: int

@dataclass
class ReplayCard:
    side: int
    slot: int
    card_with_last_patch: CardWithLastPatch

@dataclass
class ReplayStateCard:
    side: int
    slot: int
    card: Card
    attack: int
    health: int
    is_dead: bool

@dataclass
class ReplayState:
    state_num: int
    turn: int
    player1_cards: list[ReplayStateCard] = field(default_factory=list)
    player2_cards: list[ReplayStateCard] = field(default_factory=list)

@dataclass
class ReplayAction:
    action_num: int
    turn: int
    attack_side: int
    attack_slot: int
    target_slot: int
    attacker_damage: int
    target_damage: int
    is_attacker_dead: bool
    is_target_dead: bool
    before_state: Optional[ReplayState]
    after_state: Optional[ReplayState]

@dataclass
class Replay:
    replay_id: int
    player1_id: int
    player2_id: int
    player1_nickname: str
    player2_nickname: str
    winner_player_side: int
    last_patch_id: int
    matched_at: datetime
    player1_cards: list[ReplayCard] = field(default_factory=list)
    player2_cards: list[ReplayCard] = field(default_factory=list)
    actions: list[ReplayAction] = field(default_factory=list)

@dataclass
class CardStats:
    card: Card
    card_name: str
    card_image: str
    card_id: int
    attacker_damage_as_attacker: int
    target_damage_as_defender: int
    attacker_damage_as_defender: int
    target_damage_as_attacker: int
    kills_as_attacker: int
    enemy_deaths_attacking_this: int
    deaths_as_defender: int
    deaths_as_attacker: int
    matches_played: int
    matches_won: int
    matches_lost: int
    matches_drawn: int
    given_damage: int
    taken_damage: int
    total_kills: int
    total_deaths: int
    win_rate: float
    draw_rate: float
    lose_rate: float
    avg_given_damage: float
    avg_taken_damage: float
    avg_kills: float
    avg_deaths: float
    kd_ratio: float
