from .system_prompts import WORLD_GENERATION_SYSTEM_PROMPT


def generate_world_prompt() -> tuple[str, str]:
    """
    Generate a prompt for creating the initial game world.

    Returns:
        tuple[str, str]: System prompt and user prompt for world generation
    """
    system_prompt = WORLD_GENERATION_SYSTEM_PROMPT

    user_prompt = """Create the starting region for a new Sword World 2.5 campaign.
Generate a detailed description of the Alframe Continent, focusing on a specific region
where the player's adventure begins.

Include the following elements:

1. Region Name and Description: A evocative name and overview of the starting area
2. Key Settlements: 2-3 important towns, cities, or villages with brief descriptions
3. Geographic Features: Notable landmarks, terrain, and natural features
4. Central Conflict: An overarching mystery, threat, or situation that drives the campaign
5. Local Factions: 2-3 important groups, organizations, or power structures
6. Adventure Hooks: 3-4 specific quest opportunities or story starters

Make the setting feel lived-in and provide clear opportunities for adventure.
Focus on the Sword World 2.5 aesthetic: medieval fantasy with Japanese cultural influences.

Format your response as follows:

REGION NAME: [Name of the starting region]
REGION DESCRIPTION: [2-3 paragraphs describing the area]
KEY SETTLEMENTS:
- [Settlement 1]: [Brief description]
- [Settlement 2]: [Brief description]
- [Settlement 3]: [Brief description]
GEOGRAPHIC FEATURES:
- [Feature 1]: [Description]
- [Feature 2]: [Description]
- [Feature 3]: [Description]
CENTRAL CONFLICT: [Description of the main campaign driver]
LOCAL FACTIONS:
- [Faction 1]: [Description and goals]
- [Faction 2]: [Description and goals]
- [Faction 3]: [Description and goals]
ADVENTURE HOOKS:
1. [Hook 1]
2. [Hook 2]
3. [Hook 3]
4. [Hook 4]"""

    return system_prompt, user_prompt


def generate_location_prompt(location_name: str, world_context: dict) -> tuple[str, str]:
    """
    Generate a prompt for creating a detailed location description.

    Args:
        location_name (str): Name of the location to describe
        world_context (dict): Current world context for consistency

    Returns:
        tuple[str, str]: System prompt and user prompt for location generation
    """
    system_prompt = WORLD_GENERATION_SYSTEM_PROMPT

    user_prompt = f"""Create a detailed description of {location_name} within the world context: {world_context}

Include the following elements:

1. Physical Description: Architecture, layout, and notable features
2. Inhabitants: Key NPCs, population, and social dynamics
3. Points of Interest: Specific locations within the area worth exploring
4. Current Events: What's happening here right now
5. Potential Dangers: Threats or challenges present
6. Story Hooks: Opportunities for quests or adventures

Format your response clearly with descriptive, engaging prose suitable for an RPG setting."""

    return system_prompt, user_prompt
