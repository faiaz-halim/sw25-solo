from pydantic import BaseModel
from typing import Optional, List
from .attributes import ItemType


class Item(BaseModel):
    """Base item class with common attributes."""
    id: str
    name: str
    item_type: ItemType
    description: str
    value: int  # In gold pieces or equivalent
    weight: float  # In pounds or equivalent
    is_magical: bool = False
    required_strength: int = 0
    required_dexterity: int = 0
    required_level: int = 0


class Weapon(Item):
    """Weapon item with combat-specific attributes."""
    damage_dice: str  # e.g., "1d6", "2d4"
    damage_type: str  # e.g., "Slashing", "Piercing", "Bludgeoning"
    crit_range: int = 20  # Critical hit range (e.g., 19-20)
    crit_multiplier: int = 2  # Critical hit damage multiplier
    range_increment: int = 0  # For ranged weapons, in feet
    hands_required: int = 1  # 1 for one-handed, 2 for two-handed
    special_properties: List[str] = []


class Armor(Item):
    """Armor item with protection attributes."""
    armor_class: int  # AC bonus
    max_dexterity_bonus: int = 10  # Maximum Dexterity bonus allowed
    armor_penalty: int = 0  # Armor penalty to skills
    spell_failure_chance: int = 0  # Chance to fail spellcasting
    speed_reduction: int = 0  # Movement speed reduction in feet
    special_properties: List[str] = []


class Accessory(Item):
    """Accessory item (rings, amulets, etc.) with special effects."""
    stat_bonuses: dict = {}  # e.g., {"strength": 2, "dexterity": 1}
    skill_bonuses: dict = {}  # e.g., {"magic": 1, "perception": 2}
    special_abilities: List[str] = []
