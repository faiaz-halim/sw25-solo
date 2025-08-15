from ..models.character import CharacterSheet
from ..models.monster import Monster
from ..models.dice import roll_d20, roll_dice
from typing import List, Dict, Tuple, Optional
import random


class CombatManager:
    """Manages combat encounters between characters and monsters."""

    def __init__(self):
        self.combatants = []  # List of all combatants (characters and monsters)
        self.initiative_order = []  # Ordered list of combatants by initiative
        self.current_turn = 0  # Index of current combatant in initiative order
        self.is_active = False  # Whether combat is currently active

    def start_combat(self, party: List[CharacterSheet], enemies: List[Monster]) -> List[str]:
        """
        Start a combat encounter.

        Args:
            party (List[CharacterSheet]): List of player characters
            enemies (List[Monster]): List of enemy monsters

        Returns:
            List[str]: List of combat start messages
        """
        self.combatants = party + enemies
        self.initiative_order = []
        self.current_turn = 0
        self.is_active = True

        messages = ["Combat begins!"]

        # Calculate initiative
        initiative_results = self.calculate_initiative()
        self.initiative_order = [combatant for _, combatant in sorted(initiative_results, key=lambda x: x[0], reverse=True)]

        # Add initiative results to messages
        for initiative, combatant in initiative_results:
            name = combatant.name if hasattr(combatant, 'name') else f"Monster {combatant.id}"
            messages.append(f"{name} rolls initiative: {initiative}")

        current_combatant = self.initiative_order[self.current_turn]
        name = current_combatant.name if hasattr(current_combatant, 'name') else f"Monster {current_combatant.id}"
        messages.append(f"{name}'s turn begins!")

        return messages

    def calculate_initiative(self) -> List[Tuple[int, object]]:
        """
        Calculate initiative for all combatants.

        Returns:
            List[Tuple[int, object]]: List of (initiative_roll, combatant) tuples
        """
        results = []

        for combatant in self.combatants:
            # Base initiative is d20 + Dexterity modifier
            dex_modifier = combatant.dexterity // 3
            initiative_roll = roll_d20() + dex_modifier
            results.append((initiative_roll, combatant))

        return results

    def process_turn(self, action: str, target: Optional[object] = None) -> List[str]:
        """
        Process the current combatant's turn.

        Args:
            action (str): The action to take ("attack", "spell", "defend", etc.)
            target (Optional[object]): Target of the action

        Returns:
            List[str]: List of messages describing the results
        """
        if not self.is_active:
            return ["Combat is not active."]

        current_combatant = self.initiative_order[self.current_turn]
        messages = []

        if action == "attack":
            if target:
                result = self.handle_attack(current_combatant, target)
                messages.extend(result["messages"])
            else:
                messages.append("No target specified for attack.")
        elif action == "defend":
            # Increase defense for this turn
            current_combatant.defense += 2
            name = current_combatant.name if hasattr(current_combatant, 'name') else f"Monster {current_combatant.id}"
            messages.append(f"{name} takes a defensive stance.")
        else:
            messages.append(f"Unknown action: {action}")

        # Check if combat has ended
        if self.check_end_condition():
            self.is_active = False
            messages.append("Combat has ended!")
            return messages

        # Move to next turn
        self.current_turn = (self.current_turn + 1) % len(self.initiative_order)
        next_combatant = self.initiative_order[self.current_turn]
        name = next_combatant.name if hasattr(next_combatant, 'name') else f"Monster {next_combatant.id}"
        messages.append(f"{name}'s turn begins!")

        return messages

    def handle_attack(self, attacker: object, defender: object) -> Dict:
        """
        Handle an attack action between two combatants.

        Args:
            attacker (object): The attacking combatant
            defender (object): The defending combatant

        Returns:
            Dict: Dictionary containing attack results and messages
        """
        result = {"success": False, "damage": 0, "messages": []}

        # Get attacker name
        attacker_name = attacker.name if hasattr(attacker, 'name') else f"Monster {attacker.id}"
        defender_name = defender.name if hasattr(defender, 'name') else f"Monster {defender.id}"

        # Roll to hit
        attack_roll = roll_d20()
        total_attack = attack_roll + attacker.attack_bonus

        result["messages"].append(f"{attacker_name} attacks {defender_name} (Roll: {attack_roll} + {attacker.attack_bonus} = {total_attack} vs AC {defender.defense})")

        # Check if attack hits
        if attack_roll == 1:  # Natural 1 always misses
            result["messages"].append("Critical miss!")
            return result
        elif attack_roll == 20:  # Natural 20 always hits
            result["success"] = True
            result["messages"].append("Critical hit!")
        elif total_attack >= defender.defense:
            result["success"] = True
            result["messages"].append("Hit!")
        else:
            result["messages"].append("Miss!")
            return result

        # Calculate damage
        if hasattr(attacker, 'equipped_weapon') and attacker.equipped_weapon:
            damage_dice = attacker.equipped_weapon.damage_dice
        elif hasattr(attacker, 'damage_dice'):
            damage_dice = attacker.damage_dice
        else:
            damage_dice = "1d4"  # Default damage

        damage = roll_dice(damage_dice)

        # Apply damage
        defender.take_damage(damage)
        result["damage"] = damage
        result["messages"].append(f"{defender_name} takes {damage} damage! (HP: {defender.hit_points}/{defender.max_hit_points})")

        # Check if defender is defeated
        if not defender.is_alive():
            result["messages"].append(f"{defender_name} is defeated!")

        return result

    def handle_spell(self, caster: object, spell: object, target: object) -> Dict:
        """
        Handle a spell casting action.

        Args:
            caster (object): The spell caster
            spell (object): The spell being cast
            target (object): The target of the spell

        Returns:
            Dict: Dictionary containing spell results and messages
        """
        result = {"success": True, "messages": []}

        caster_name = caster.name if hasattr(caster, 'name') else f"Monster {caster.id}"
        target_name = target.name if hasattr(target, 'name') else f"Monster {target.id}"

        result["messages"].append(f"{caster_name} casts {spell.name} on {target_name}!")

        # Check if caster has enough MP
        if hasattr(caster, 'magic_points') and caster.magic_points >= spell.mp_cost:
            caster.magic_points -= spell.mp_cost
            result["messages"].append(f"{caster_name} spends {spell.mp_cost} MP.")
        else:
            result["messages"].append(f"{caster_name} doesn't have enough MP to cast {spell.name}!")
            result["success"] = False
            return result

        # Apply spell effects (simplified)
        if "heal" in spell.name.lower():
            # Healing spell
            heal_amount = roll_dice("2d6")
            if hasattr(target, 'hit_points'):
                target.hit_points = min(target.max_hit_points, target.hit_points + heal_amount)
                result["messages"].append(f"{target_name} is healed for {heal_amount} HP! (HP: {target.hit_points}/{target.max_hit_points})")
        else:
            # Damage spell
            damage = roll_dice("2d6")
            if hasattr(target, 'take_damage'):
                target.take_damage(damage)
                result["messages"].append(f"{target_name} takes {damage} damage! (HP: {target.hit_points}/{target.max_hit_points})")

                if not target.is_alive():
                    result["messages"].append(f"{target_name} is defeated!")

        return result

    def check_end_condition(self) -> bool:
        """
        Check if combat has ended (one side defeated).

        Returns:
            bool: True if combat has ended, False otherwise
        """
        # Check if all party members are defeated
        party_alive = any(combatant.is_alive() for combatant in self.combatants
                         if isinstance(combatant, CharacterSheet))

        # Check if all enemies are defeated
        enemies_alive = any(combatant.is_alive() for combatant in self.combatants
                           if isinstance(combatant, Monster))

        # Combat ends when one side is completely defeated
        return not party_alive or not enemies_alive

    def get_combat_status(self) -> Dict:
        """
        Get the current status of the combat.

        Returns:
            Dict: Dictionary containing combat status information
        """
        return {
            "is_active": self.is_active,
            "current_turn": self.current_turn,
            "combatants": [
                {
                    "name": combatant.name if hasattr(combatant, 'name') else f"Monster {combatant.id}",
                    "hp": combatant.hit_points,
                    "max_hp": combatant.max_hit_points,
                    "is_alive": combatant.is_alive()
                }
                for combatant in self.combatants
            ],
            "initiative_order": [
                combatant.name if hasattr(combatant, 'name') else f"Monster {combatant.id}"
                for combatant in self.initiative_order
            ]
        }
