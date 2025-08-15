from ..models.character import CharacterSheet
from ..models.attributes import SkillType
from ..models.dice import roll_d20


def perform_skill_check(character: CharacterSheet, skill: SkillType, difficulty: int) -> bool:
    """
    Perform a skill check for a character.

    Args:
        character (CharacterSheet): The character attempting the skill check
        skill (SkillType): The skill being tested
        difficulty (int): The difficulty class (DC) to beat

    Returns:
        bool: True if the skill check succeeds, False otherwise
    """
    # Get the character's skill level for the specified skill
    skill_level = character.skills.get(skill, 0)

    # Roll a d20 and add the skill level
    roll = roll_d20()
    total = roll + skill_level

    # Check if the total meets or exceeds the difficulty
    return total >= difficulty


def perform_ability_check(character: CharacterSheet, ability: str, difficulty: int) -> bool:
    """
    Perform an ability check for a character.

    Args:
        character (CharacterSheet): The character attempting the ability check
        ability (str): The ability being tested (strength, dexterity, vitality, intelligence, spirit)
        difficulty (int): The difficulty class (DC) to beat

    Returns:
        bool: True if the ability check succeeds, False otherwise
    """
    # Get the character's ability score
    ability_score = getattr(character, ability.lower(), 10)  # Default to 10 if not found

    # Calculate ability modifier (ability score / 3, rounded down)
    ability_modifier = ability_score // 3

    # Roll a d20 and add the ability modifier
    roll = roll_d20()
    total = roll + ability_modifier

    # Check if the total meets or exceeds the difficulty
    return total >= difficulty
