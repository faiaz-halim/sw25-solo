from enum import Enum


class SkillType(Enum):
    """Enumeration of character skills based on Sword World 2.5 rules."""
    # Physical skills
    SWORD = "Sword"
    AXE = "Axe"
    SPEAR = "Spear"
    BOW = "Bow"
    THROWING = "Throwing"
    ARMOR = "Armor"
    DODGE = "Dodge"
    STEALTH = "Stealth"
    LOCKPICKING = "Lockpicking"
    TRAP_DISARM = "Trap Disarm"

    # Mental skills
    MAGIC = "Magic"
    HEALING = "Healing"
    IDENTIFY = "Identify Magic"
    LANGUAGE = "Language"
    KNOWLEDGE = "Knowledge"
    PERCEPTION = "Perception"
    SURVIVAL = "Survival"
    BARGAIN = "Bargain"
    CHARM = "Charm"

    # Social skills
    INTIMIDATE = "Intimidate"
    PERSUADE = "Persuade"
    DECEIVE = "Deceive"
    PERFORMANCE = "Performance"
    LEADERSHIP = "Leadership"


class Race(Enum):
    """Enumeration of character races based on Sword World 2.5 rules."""
    HUMAN = "Human"
    ELF = "Elf"
    DWARF = "Dwarf"
    GNOME = "Gnome"
    HALFLING = "Halfling"
    HALF_ELF = "Half-Elf"
    HALF_DWARF = "Half-Dwarf"


class Class(Enum):
    """Enumeration of character classes based on Sword World 2.5 rules."""
    FIGHTER = "Fighter"
    WIZARD = "Wizard"
    PRIEST = "Priest"
    ROGUE = "Rogue"
    RANGER = "Ranger"
    PALADIN = "Paladin"
    BARD = "Bard"
    DRUID = "Druid"
    MONK = "Monk"
    PSIONIC = "Psionic"


class ItemType(Enum):
    """Enumeration of item types."""
    WEAPON = "Weapon"
    ARMOR = "Armor"
    SHIELD = "Shield"
    ACCESSORY = "Accessory"
    CONSUMABLE = "Consumable"
    MAGIC_ITEM = "Magic Item"
    QUEST_ITEM = "Quest Item"
    MISC = "Miscellaneous"
