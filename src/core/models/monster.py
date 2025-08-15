from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from .attributes import SkillType
from .item import Item


class Monster(BaseModel):
    """Monster data class with stats, abilities, and loot tables based on Sword World 2.5 rules."""
    id: str
    name: str
    level: int  # Monster level
    hit_points: int
    max_hit_points: int
    magic_points: int
    max_magic_points: int
    defense: int
    attack_bonus: int

    # Core attributes
    strength: int
    dexterity: int
    vitality: int
    intelligence: int
    spirit: int

    # Skills
    skills: Dict[SkillType, int]  # Skill type to skill level

    # Combat attributes
    damage_dice: str  # e.g., "1d6", "2d4"
    damage_type: str  # e.g., "Slashing", "Piercing", "Bludgeoning"
    crit_range: int = 20  # Critical hit range (e.g., 19-20)
    crit_multiplier: int = 2  # Critical hit damage multiplier

    # Special abilities
    special_abilities: List[str] = []  # e.g., "Fire Breath", "Invisibility"
    immunities: List[str] = []  # e.g., "Fire", "Poison"
    vulnerabilities: List[str] = []  # e.g., "Cold", "Holy"

    # Loot
    loot_table: List[Dict[str, Any]] = []  # List of possible loot items with drop chances
    experience_reward: int  # Experience points awarded for defeating this monster

    # Monster behavior
    alignment: str = "Neutral"
    habitat: str = "Unknown"  # Where this monster is typically found
    description: str = ""  # Detailed description of the monster

    def is_alive(self) -> bool:
        """Check if the monster is still alive."""
        return self.hit_points > 0

    def take_damage(self, amount: int) -> bool:
        """Apply damage to the monster. Returns True if monster is still alive."""
        self.hit_points -= amount
        return self.is_alive()
