from pydantic import BaseModel
from typing import List, Dict, Optional
from .attributes import Race, Class, SkillType
from .item import Item, Weapon, Armor, Accessory
from .spell import Spell


class CharacterSheet(BaseModel):
    """Character sheet implementation based on Sword World 2.5 rules."""
    # Basic information
    id: str
    name: str
    race: Race
    character_class: Class
    level: int = 1
    experience_points: int = 0

    # Core attributes
    strength: int
    dexterity: int
    vitality: int
    intelligence: int
    spirit: int

    # Derived stats
    hit_points: int
    max_hit_points: int
    magic_points: int
    max_magic_points: int
    defense: int
    attack_bonus: int

    # Skills
    skills: Dict[SkillType, int]  # Skill type to skill level

    # Spells
    spells: List[Spell] = []

    # Inventory and equipment
    inventory: List[Item] = []
    equipped_weapon: Optional[Weapon] = None
    equipped_armor: Optional[Armor] = None
    equipped_accessories: List[Accessory] = []

    # Character background
    backstory: str = ""
    alignment: str = "Neutral"

    def calculate_derived_stats(self):
        """Calculate derived stats based on attributes and equipment."""
        # HP calculation based on class and vitality
        base_hp = 0
        if self.character_class == Class.FIGHTER:
            base_hp = 10 + max(1, self.vitality // 2)
        elif self.character_class == Class.WIZARD:
            base_hp = 4 + max(1, self.vitality // 4)
        elif self.character_class == Class.PRIEST:
            base_hp = 6 + max(1, self.vitality // 3)
        else:
            base_hp = 8 + max(1, self.vitality // 3)

        # Add level-based HP
        self.max_hit_points = base_hp + (self.level - 1) * max(1, self.vitality // 3)
        if self.hit_points > self.max_hit_points:
            self.hit_points = self.max_hit_points

        # MP calculation based on class and intelligence/spirit
        if self.character_class in [Class.WIZARD, Class.PRIEST]:
            base_mp = 6 + max(1, (self.intelligence if self.character_class == Class.WIZARD else self.spirit) // 2)
            self.max_magic_points = base_mp + (self.level - 1) * max(1, (self.intelligence if self.character_class == Class.WIZARD else self.spirit) // 3)
        else:
            self.max_magic_points = 0

        if self.magic_points > self.max_magic_points:
            self.magic_points = self.max_magic_points

        # Defense calculation
        base_defense = 10 + self.dexterity // 2
        armor_bonus = self.equipped_armor.armor_class if self.equipped_armor else 0
        self.defense = base_defense + armor_bonus

        # Attack bonus calculation
        base_attack = self.level // 2
        strength_bonus = self.strength // 3
        self.attack_bonus = base_attack + strength_bonus

    def equip_item(self, item: Item):
        """Equip an item and update character stats."""
        if item.item_type == "Weapon" and isinstance(item, Weapon):
            self.equipped_weapon = item
        elif item.item_type == "Armor" and isinstance(item, Armor):
            self.equipped_armor = item
        elif item.item_type == "Accessory" and isinstance(item, Accessory):
            if len(self.equipped_accessories) < 2:  # Assume max 2 accessories
                self.equipped_accessories.append(item)
            else:
                raise ValueError("Cannot equip more than 2 accessories")
        else:
            raise ValueError(f"Cannot equip item of type {item.item_type}")

        self.calculate_derived_stats()

    def unequip_item(self, item: Item):
        """Unequip an item and update character stats."""
        if item == self.equipped_weapon:
            self.equipped_weapon = None
        elif item == self.equipped_armor:
            self.equipped_armor = None
        elif item in self.equipped_accessories:
            self.equipped_accessories.remove(item)
        else:
            raise ValueError("Item is not equipped")

        self.calculate_derived_stats()

    def take_damage(self, amount: int) -> bool:
        """Apply damage to the character. Returns True if character is still alive."""
        self.hit_points -= amount
        return self.is_alive()

    def is_alive(self) -> bool:
        """Check if the character is still alive."""
        return self.hit_points > 0

    def add_item_to_inventory(self, item: Item):
        """Add an item to the character's inventory."""
        self.inventory.append(item)

    def remove_item_from_inventory(self, item: Item) -> bool:
        """Remove an item from the character's inventory. Returns True if successful."""
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False
