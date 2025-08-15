from .system_prompts import NPC_INTERACTION_SYSTEM_PROMPT


def generate_npc_dialogue_prompt(npc_personality: dict, player_dialogue: str, game_context: dict) -> tuple[str, str]:
    """
    Generate a prompt for creating dynamic NPC dialogue.

    Args:
        npc_personality (dict): NPC's personality traits and background
        player_dialogue (str): Player's dialogue input
        game_context (dict): Current game context for relevance

    Returns:
        tuple[str, str]: System prompt and user prompt for NPC dialogue generation
    """
    system_prompt = NPC_INTERACTION_SYSTEM_PROMPT

    user_prompt = f"""Roleplay as an NPC with the following characteristics:

Name: {npc_personality.get('name', 'Unknown')}
Race: {npc_personality.get('race', 'Human')}
Role/Profession: {npc_personality.get('role', 'Commoner')}
Personality Traits: {', '.join(npc_personality.get('traits', []))}
Motivations: {', '.join(npc_personality.get('motivations', []))}
Background: {npc_personality.get('background', 'Unknown')}
Current Mood: {npc_personality.get('mood', 'neutral')}

Current Game Context:
Location: {game_context.get('location', 'Unknown')}
Player Character: {game_context.get('player_name', 'Unknown')}
Relationship with Player: {game_context.get('relationship', 'stranger')}
Current Quests: {', '.join(game_context.get('active_quests', []))}

Player Says: "{player_dialogue}"

Respond in character as this NPC. Your response should:
1. Reflect the NPC's personality, background, and current mood
2. Be appropriate to the player's dialogue and the current situation
3. Provide useful information, quest hooks, or interesting roleplay opportunities
4. Advance the story or relationship with the player
5. Include the NPC's motivations and goals in their response
6. Use speech patterns and mannerisms fitting the NPC's character

Keep the response natural and engaging, typically 2-4 sentences."""

    return system_prompt, user_prompt


def generate_npc_personality_prompt(npc_template: dict) -> tuple[str, str]:
    """
    Generate a prompt for creating detailed NPC personality traits.

    Args:
        npc_template (dict): Basic NPC information (name, role, etc.)

    Returns:
        tuple[str, str]: System prompt and user prompt for NPC personality generation
    """
    system_prompt = NPC_INTERACTION_SYSTEM_PROMPT

    user_prompt = f"""Create detailed personality traits for an NPC with the following basic information:

Name: {npc_template.get('name', 'Unknown')}
Race: {npc_template.get('race', 'Human')}
Role/Profession: {npc_template.get('role', 'Commoner')}
Location: {npc_template.get('location', 'Unknown')}
Initial Relationship: {npc_template.get('relationship', 'stranger')}

Generate the following personality elements:

1. Core Personality Traits: 3-5 key character traits that define their personality
2. Speech Patterns: How they talk, vocabulary, accent, or mannerisms
3. Motivations: What drives them, their goals and desires
4. Fears/Flaws: Character weaknesses or things they're afraid of
5. Background: Brief history that explains their current situation
6. Mood: Current emotional state (can change during interactions)
7. Quirks: Unique habits, behaviors, or physical mannerisms
8. Attitude toward Player: How they initially view the player character

Make the NPC feel like a real person with depth and complexity.
Consider how their role and location influence their personality.
Focus on the Sword World 2.5 setting and cultural elements."""

    return system_prompt, user_prompt


def generate_npc_reaction_prompt(npc_state: dict, player_action: str, context: str) -> tuple[str, str]:
    """
    Generate a prompt for creating NPC reactions to player actions.

    Args:
        npc_state (dict): Current NPC state and personality
        player_action (str): Player's recent action
        context (str): Context for why the action matters

    Returns:
        tuple[str, str]: System prompt and user prompt for NPC reaction generation
    """
    system_prompt = NPC_INTERACTION_SYSTEM_PROMPT

    user_prompt = f"""Roleplay as {npc_state.get('name', 'Unknown')} and react to the player's recent action:

Player Action: "{player_action}"
Context: {context}

NPC State:
Personality: {', '.join(npc_state.get('traits', []))}
Current Mood: {npc_state.get('mood', 'neutral')}
Relationship with Player: {npc_state.get('relationship', 'stranger')}
Motivations: {', '.join(npc_state.get('motivations', []))}

React to the player's action with:
1. An immediate emotional and verbal response
2. Description of any physical reactions or changes in demeanor
3. How this action affects the NPC's relationship with the player
4. Any new information or opportunities that arise from this interaction
5. Clear indication of what the player can do next

Keep the reaction natural and in character, reflecting the NPC's personality and the significance of the player's action."""

    return system_prompt, user_prompt


def generate_shopkeeper_prompt(shop_inventory: list, npc_personality: dict, player_character: dict) -> tuple[str, str]:
    """
    Generate a prompt for creating shopkeeper NPC interactions.

    Args:
        shop_inventory (list): Available items for sale
        npc_personality (dict): Shopkeeper's personality traits
        player_character (dict): Player character information

    Returns:
        tuple[str, str]: System prompt and user prompt for shopkeeper interaction
    """
    system_prompt = NPC_INTERACTION_SYSTEM_PROMPT

    inventory_text = "\n".join([f"- {item.get('name', 'Unknown Item')}: {item.get('value', 0)} gold" for item in shop_inventory])

    user_prompt = f"""Roleplay as a shopkeeper NPC with the following characteristics:

Name: {npc_personality.get('name', 'Shopkeeper')}
Personality Traits: {', '.join(npc_personality.get('traits', []))}
Business Philosophy: {npc_personality.get('business_philosophy', 'Standard merchant')}
Attitude toward Customers: {npc_personality.get('customer_attitude', 'Professional')}

Shop Inventory:
{inventory_text}

Player Character: {player_character.get('name', 'Unknown')} (Level {player_character.get('level', 1)})

Roleplay as this shopkeeper interacting with the player. Your response should:
1. Reflect your personality and business approach
2. Offer relevant items from your inventory
3. Provide shop-related dialogue (greetings, haggling, rumors, etc.)
4. Include your personal opinions or knowledge about items
5. Respond appropriately to the player's requests or questions
6. Maintain your character's voice and mannerisms

Keep the interaction engaging and provide a realistic shopping experience."""

    return system_prompt, user_prompt
