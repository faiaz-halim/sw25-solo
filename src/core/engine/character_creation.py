from ..models.character import CharacterSheet
from ..models.attributes import Race, Class, SkillType
from ..models.dice import roll_d6, roll_2d6
from typing import Dict, List
import random


def roll_on_history_table() -> str:
    """
    Roll on the History Table A [p. 52] to generate character background elements.

    Returns:
        str: Description of the character's background/history
    """
    # Simplified history table based on typical Sword World 2.5 tables
    history_table = [
        "Noble birth - You were born into a noble family with wealth and influence.",
        "Common birth - You were born into a common family, learning hard work and humility.",
        "Military background - You served in the military, learning discipline and combat.",
        "Academic pursuit - You studied in schools or under mentors, gaining knowledge.",
        "Criminal past - You lived a life of crime, learning stealth and deception.",
        "Religious upbringing - You were raised in a temple, learning faith and healing.",
        "Wandering life - You traveled extensively, learning about different cultures.",
        "Tragic loss - You suffered a great loss that shaped your worldview.",
        "Mysterious origins - Your past is shrouded in mystery, even to yourself.",
        "Artistic talent - You were trained in arts, music, or performance.",
        "Craftsman's apprentice - You learned a trade or craft from a young age.",
        "Survivor's instinct - You lived through hardship, developing resilience."
    ]

    roll = roll_2d6()
    # Map 2d6 roll (2-12) to history table indices (0-11)
    index = min(max(roll - 2, 0), 11)
    return history_table[index]


def roll_on_adventure_reason_table() -> str:
    """
    Roll on the Adventure Reason Table to determine why the character seeks adventure.

    Returns:
        str: Reason for seeking adventure
    """
    adventure_reasons = [
        "Destiny calls - You feel a calling to a greater purpose.",
        "Revenge - You seek to avenge a wrong done to you or your family.",
        "Wealth - You need money to solve personal problems or desires.",
        "Knowledge - You seek to learn ancient secrets or forbidden knowledge.",
        "Protection - You must protect someone or something important.",
        "Redemption - You seek to atone for past mistakes.",
        "Curiosity - You are driven by an insatiable desire to explore.",
        "Duty - You have an obligation to your people, family, or order.",
        "Love - You search for someone or something dear to your heart.",
        "Power - You crave strength and influence in the world.",
        "Justice - You fight against evil and injustice wherever you find it.",
        "Escape - You flee from a dangerous situation or unwanted responsibility."
    ]

    roll = roll_2d6()
    # Map 2d6 roll (2-12) to adventure reasons indices (0-11)
    index = min(max(roll - 2, 0), 11)
    return adventure_reasons[index]


def generate_starting_attributes(race: Race, character_class: Class) -> Dict[str, int]:
    """
    Generate starting attributes based on race and class.

    Args:
        race (Race): Character's race
        character_class (Class): Character's class

    Returns:
        Dict[str, int]: Dictionary of attribute names to values
    """
    # Base attributes (3d6 for each)
    attributes = {
        "strength": sum(roll_d6() for _ in range(3)),
        "dexterity": sum(roll_d6() for _ in range(3)),
        "vitality": sum(roll_d6() for _ in range(3)),
        "intelligence": sum(roll_d6() for _ in range(3)),
        "spirit": sum(roll_d6() for _ in range(3))
    }

    # Apply racial modifiers
    if race == Race.HUMAN:
        # Humans get +1 to all attributes
        for attr in attributes:
            attributes[attr] += 1
    elif race == Race.ELF:
        # Elves get +1 Dexterity, +1 Intelligence, -1 Vitality
        attributes["dexterity"] += 1
        attributes["intelligence"] += 1
        attributes["vitality"] -= 1
    elif race == Race.DWARF:
        # Dwarves get +1 Strength, +1 Vitality, -1 Dexterity
        attributes["strength"] += 1
        attributes["vitality"] += 1
        attributes["dexterity"] -= 1
    elif race == Race.HALFLING:
        # Halflings get +1 Dexterity, +1 Spirit, -1 Strength
        attributes["dexterity"] += 1
        attributes["spirit"] += 1
        attributes["strength"] -= 1

    # Apply class modifiers (simplified)
    if character_class == Class.FIGHTER:
        attributes["strength"] += 2
        attributes["vitality"] += 1
    elif character_class == Class.WIZARD:
        attributes["intelligence"] += 2
        attributes["spirit"] += 1
    elif character_class == Class.PRIEST:
        attributes["spirit"] += 2
        attributes["vitality"] += 1
    elif character_class == Class.ROGUE:
        attributes["dexterity"] += 2
        attributes["intelligence"] += 1

    # Ensure no attribute goes below 1
    for attr in attributes:
        attributes[attr] = max(1, attributes[attr])

    return attributes


def generate_starting_skills(character_class: Class) -> Dict[SkillType, int]:
    """
    Generate starting skills based on character class.

    Args:
        character_class (Class): Character's class

    Returns:
        Dict[SkillType, int]: Dictionary of skill types to skill levels
    """
    skills = {}

    # Base skills everyone gets
    base_skills = [SkillType.PERCEPTION, SkillType.SURVIVAL, SkillType.BARGAIN]
    for skill in base_skills:
        skills[skill] = 1

    # Class-specific skills
    if character_class == Class.FIGHTER:
        skills[SkillType.SWORD] = 2
        skills[SkillType.ARMOR] = 2
        skills[SkillType.DODGE] = 1
    elif character_class == Class.WIZARD:
        skills[SkillType.MAGIC] = 3
        skills[SkillType.KNOWLEDGE] = 2
        skills[SkillType.LANGUAGE] = 1
    elif character_class == Class.PRIEST:
        skills[SkillType.HEALING] = 2
        skills[SkillType.CHARM] = 2
        skills[SkillType.KNOWLEDGE] = 1
    elif character_class == Class.ROGUE:
        skills[SkillType.STEALTH] = 3
        skills[SkillType.LOCKPICKING] = 2
        skills[SkillType.DECEIVE] = 1

    return skills


def create_new_character(name: str, race: Race, character_class: Class) -> CharacterSheet:
    """
    Create a new character with generated attributes, skills, and background.

    Args:
        name (str): Character's name
        race (Race): Character's race
        character_class (Class): Character's class

    Returns:
        CharacterSheet: Fully created character sheet
    """
    # Generate attributes
    attributes = generate_starting_attributes(race, character_class)

    # Generate skills
    skills = generate_starting_skills(character_class)

    # Generate background
    history = roll_on_history_table()
    adventure_reason = roll_on_adventure_reason_table()
    backstory = f"{history} {adventure_reason}"

    # Create character sheet
    character = CharacterSheet(
        id=f"char_{random.randint(1000, 9999)}",
        name=name,
        race=race,
        character_class=character_class,
        level=1,
        experience_points=0,
        strength=attributes["strength"],
        dexterity=attributes["dexterity"],
        vitality=attributes["vitality"],
        intelligence=attributes["intelligence"],
        spirit=attributes["spirit"],
        hit_points=10,  # Will be calculated properly
        max_hit_points=10,
        magic_points=0,  # Will be calculated properly
        max_magic_points=0,
        defense=10,  # Will be calculated properly
        attack_bonus=0,  # Will be calculated properly
        skills=skills,
        spells=[],
        inventory=[],
        equipped_weapon=None,
        equipped_armor=None,
        equipped_accessories=[],
        backstory=backstory,
        alignment="Neutral"
    )

    # Calculate derived stats
    character.calculate_derived_stats()

    return character
