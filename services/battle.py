import random
from dataclasses import dataclass
import database.database as db
from models.models import *

장갑 = 1
방어 = 2
비행 = 3
공격불가 = 4
독성 = 5
돌진 = 6
도약 = 7
잠수 = 8


class Slot:
    def __init__(self, side: int, slot: int, card_id: int, attack:int, max_hp:int, 
                 abilities:tuple[int, ...], enemy_team:list["Slot"]):
        self.side = side
        self.slot = slot
        self.card_id = card_id
        self.attack = attack
        self.max_hp = max_hp
        self.hp = max_hp
        self.abilities = abilities
        self.enemy_team = enemy_team
        self.is_dead = False
        self.attacked_first = False
    
    def choose_target(self, targets: list["Slot"]):
        targets = [x for x in targets if not x.is_dead]
        if 비행 not in self.abilities:
            targets = [x for x in targets if 비행 not in x.abilities]
        defense_targets = [x for x in targets if 방어 in x.abilities]
        if defense_targets:
            targets = defense_targets
        if not targets or 공격불가 in self.abilities:
            return None
        targets.sort(key=lambda x: x.slot)
        if 잠수 in self.abilities and 도약 in self.abilities:
            return random.choice(targets)
        elif 잠수 in self.abilities:
            return targets[0]
        elif 도약 in self.abilities:
            return targets[-1]
        else:
            return random.choice(targets)

    def attack_target(self, target: "Slot"):
        total_attack = max(self.attack, 0)
        if 장갑 in target.abilities:
            total_attack = max(total_attack - 2, 0)
        target.hp = max(target.hp - total_attack, 0)
        if not self.attacked_first and total_attack > 0 and 독성 in self.abilities:
            target.hp = 0
        total_damage = max(target.attack, 0)
        if 장갑 in self.abilities:
            total_damage = max(total_damage - 2, 0)
        self.hp = max(self.hp - total_damage, 0)
        if not self.attacked_first:
            self.attacked_first = True
        
        return (total_attack, total_damage, self.check_death(), target.check_death())

    def check_death(self):
        if self.hp <= 0:
            self.is_dead = True
            return True
        return False

class Game:
    def __init__(
        self,
        player1: DeckAccount,
        player2: DeckAccount
    ):
        
        player1_card = [x.card for x in player1.cards]
        player2_card = [x.card for x in player2.cards]
        self.player1_cards: list[Slot] = []
        self.player2_cards: list[Slot] = []

        for idx, card in enumerate(player1_card):
            self.player1_cards.append(
                Slot(
                    side=1,
                    slot=idx,
                    card_id=card.card_id,
                    attack=card.attack,
                    max_hp=card.health,
                    abilities=[x.ability_id for x in card.abilities],
                    enemy_team=self.player2_cards,
                )
            )

        for idx, card in enumerate(player2_card):
            self.player2_cards.append(
                Slot(
                    side=2,
                    slot=idx,
                    card_id=card.card_id,
                    attack=card.attack,
                    max_hp=card.health,
                    abilities=[x.ability_id for x in card.abilities],
                    enemy_team=self.player1_cards,
                )
            )
        

        self.match_states = []
        self.match_state_cards = []
        self.match_actions = []
        self.turn = 0
        self.state_num = 0
        self.action_num = 1


    def check_player1_dead(self):
        return all(card.is_dead for card in self.player1_cards)
    
    def check_player2_dead(self):
        return all(card.is_dead for card in self.player2_cards)

    def check_game_over(self):
        return self.turn > 100 or self.check_player1_dead() or self.check_player2_dead()

    def charge_attack(self):
        charge_attackers = [x for x in self.player1_cards + self.player2_cards if 돌진 in x.abilities]
        for charge_attacker in charge_attackers: 
            if self.check_game_over():
                return       
            if not charge_attacker.is_dead:
                self.slot_attack(charge_attacker)
    
    def slot_attack(self, attacker: Slot):
        attack_target = attacker.choose_target(attacker.enemy_team)
        if attack_target == None:
            return
        before_state = self.state_num
        total_attack, total_damage, attacker_dead, target_dead = attacker.attack_target(attack_target)
        
        self.save_state()
        after_state = self.state_num
        self.match_actions.append(MatchAction(self.action_num, self.turn, attacker.side, attacker.slot, attack_target.slot,
                                              total_attack, total_damage, attacker_dead, target_dead,
                                              before_state, after_state))
        self.action_num += 1
    
    def save_state(self):
        self.state_num += 1
        self.match_states.append(MatchState(self.state_num, self.turn))
        for card in self.player1_cards:
            self.match_state_cards.append(MatchStateCard(self.state_num, card.side, card.slot, card.card_id, card.attack, card.hp, card.is_dead))
        for card in self.player2_cards:
            self.match_state_cards.append(MatchStateCard(self.state_num, card.side, card.slot, card.card_id, card.attack, card.hp, card.is_dead))
            
    def run(self, last_patch_id: int):
        self.save_state()
        self.charge_attack()
        attack_order = sorted(self.player1_cards + self.player2_cards, key=lambda x: (x.slot, -x.side))
        is_game_over = self.check_game_over()
        for _ in range(1000):
            self.turn += 1
            for slot in attack_order:
                if slot.is_dead:
                    continue
                self.slot_attack(slot)
                if self.check_game_over():
                    is_game_over = True
                    break
            if is_game_over:
                break
        result = 3
        if self.check_player1_dead():
            result -= 1
        if self.check_player2_dead():
            result -= 2

        return MatchResult (
            result = result,
            match_states = self.match_states,
            match_state_cards = self.match_state_cards,
            match_actions = self.match_actions,
            matched_at = datetime.now(),
            last_patch_id = last_patch_id
        )



