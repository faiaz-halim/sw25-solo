from .system_prompts import CHARACTER_GENERATION_SYSTEM_PROMPT
from ...core.models.attributes import Race, Class


def generate_backstory_prompt(race: Race, character_class: Class, history_elements: dict) -> tuple[str, str]:
    """
    Generate a prompt for creating a character's backstory.

    Args:
        race (Race): Character's race
        character_class (Class): Character's class
        history_elements (dict): Results from history table rolls

    Returns:
        tuple[str, str]: System prompt and user prompt for backstory generation
    """
    system_prompt = CHARACTER_GENERATION_SYSTEM_PROMPT

    user_prompt = f"""Create a detailed backstory for a {race.value} {character_class.value} based on the following background elements:

Background Elements:
- History: {history_elements.get('history', 'Unknown')}
- Adventure Reason: {history_elements.get('adventure_reason', 'Unknown')}

Create a compelling 3-4 paragraph origin story that:

1. Weaves together the character's racial and class background with their history
2. Explains their motivation for seeking adventure
3. Includes specific details like names, places, and formative events
4. Adds personality traits and quirks that make the character memorable
5. Provides hooks for future adventures and connections to the game world

Make the backstory feel natural and provide clear motivations for the character's current situation.
Focus on the Sword World 2.5 setting and cultural elements.

Format your response as a coherent narrative without section headers."""

    return system_prompt, user_prompt


def generate_personality_prompt(race: Race, character_class: Class, backstory: str) -> tuple[str, str]:
    """
    Generate a prompt for creating a character's personality traits.

    Args:
        race (Race): Character's race
        character_class (Class): Character's class
        backstory (str): Character's backstory for context

    Returns:
        tuple[str, str]: System prompt and user prompt for personality generation
    """
    system_prompt = CHARACTER_GENERATION_SYSTEM_PROMPT

    user_prompt = f"""Based on this {race.value} {character_class.value} backstory:

{backstory}

Generate 5-7 key personality traits and characteristics for this character, including:

1. Core Personality Traits: 2-3 fundamental character traits
2. Quirks and Habits: Specific behaviors or mannerisms
3. Beliefs and Values: What the character holds important
4. Fears and Weaknesses: Character flaws or vulnerabilities
5. Social Tendencies: How they interact with others
6. Combat Attitude: How they approach conflicts
7. Special Interests: Hobbies, knowledge areas, or passions

Format your response as a clear list of traits with brief explanations."""

    return system_prompt, user_prompt


def generate_appearance_prompt(race: Race, character_class: Class, personality_traits: list) -> tuple[str, str]:
    """
    Generate a prompt for creating a character's physical appearance.

    Args:
        race (Race): Character's race
        character_class (Class): Character's class
        personality_traits (list): Character's personality traits for context

    Returns:
        tuple[str, str]: System prompt and user prompt for appearance generation
    """
    system_prompt = CHARACTER_GENERATION_SYSTEM_PROMPT

    traits_text = "\n".join(f"- {trait}" for trait in personality_traits)

    user_prompt = f"""Based on this {race.value} {character_class.value} with the following personality traits:

{traits_text}

Generate a detailed physical appearance description including:

1. General Build and Stature: Height, weight, overall physique
2. Facial Features: Face shape, eyes, hair, distinctive marks
3. Skin and Complexion: Color, texture, notable features
4. Clothing and Gear: Typical attire and equipment
5. Distinguishing Features: Scars, tattoos, jewelry, or unique markings
6. Movement and Posture: How they carry themselves
7. Overall Impression: The immediate visual impact they make

Focus on the Sword World 2.5 aesthetic and how the character's background might influence their appearance.
Format your response as a coherent descriptive paragraph."""

    return system_prompt, user_prompt
