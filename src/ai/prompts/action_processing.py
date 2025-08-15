from .system_prompts import ACTION_PROCESSING_SYSTEM_PROMPT


def generate_action_prompt(game_state: dict, player_input: str) -> tuple[str, str]:
    """
    Generate a prompt for processing a player's action.

    Args:
        game_state (dict): Current game state for context
        player_input (str): Player's action input

    Returns:
        tuple[str, str]: System prompt and user prompt for action processing
    """
    system_prompt = ACTION_PROCESSING_SYSTEM_PROMPT

    user_prompt = f"""Process the player's action in the context of the current game state:

Player Action: "{player_input}"

Current Game State:
Location: {game_state.get('world_context', {}).get('current_location', 'Unknown')}
Description: {game_state.get('world_context', {}).get('world_description', 'Unknown')}
Time of Day: {game_state.get('world_context', {}).get('time_of_day', 'day')}
Weather: {game_state.get('world_context', {}).get('weather', 'clear')}
Player Character: {game_state.get('player_character', {}).get('name', 'Unknown')} (Level {game_state.get('player_character', {}).get('level', 1)} {game_state.get('player_character', {}).get('character_class', 'Unknown')})
Party Members: {', '.join([member.get('name', 'Unknown') for member in game_state.get('party_members', [])])}
Active Quests: {len(game_state.get('active_quests', []))}

Respond to the player's action with:
1. An immediate narrative description of what happens
2. The consequences or results of their action
3. New options or choices that arise from the outcome
4. Any skill checks, combat, or special events that occur

Be descriptive but concise. Focus on the Sword World 2.5 setting and maintain the adventure atmosphere.
If the action requires a skill check or combat, describe the situation clearly but don't resolve the mechanical outcomes."""

    return system_prompt, user_prompt


def generate_exploration_prompt(game_state: dict, exploration_type: str) -> tuple[str, str]:
    """
    Generate a prompt for processing exploration actions.

    Args:
        game_state (dict): Current game state for context
        exploration_type (str): Type of exploration (search, investigate, etc.)

    Returns:
        tuple[str, str]: System prompt and user prompt for exploration processing
    """
    system_prompt = ACTION_PROCESSING_SYSTEM_PROMPT

    user_prompt = f"""Process the player's {exploration_type} action in the current location:

Current Location: {game_state.get('world_context', {}).get('current_location', 'Unknown')}
Description: {game_state.get('world_context', {}).get('world_description', 'Unknown')}

Describe what the player discovers or notices during their {exploration_type}. Include:
- Specific details they find through careful observation
- Potential clues, items, or points of interest
- Environmental storytelling elements
- Any hidden dangers or secrets
- New questions or mysteries that arise

Make the exploration feel rewarding and provide meaningful information or discoveries."""

    return system_prompt, user_prompt


def generate_combat_action_prompt(game_state: dict, combat_state: dict, player_action: str) -> tuple[str, str]:
    """
    Generate a prompt for processing combat actions.

    Args:
        game_state (dict): Current game state for context
        combat_state (dict): Current combat state
        player_action (str): Player's combat action

    Returns:
        tuple[str, str]: System prompt and user prompt for combat action processing
    """
    system_prompt = ACTION_PROCESSING_SYSTEM_PROMPT

    user_prompt = f"""Process the player's combat action in the current battle:

Player Action: "{player_action}"

Combat State:
Player Character: {game_state.get('player_character', {}).get('name', 'Unknown')}
Party Members: {', '.join([member.get('name', 'Unknown') for member in game_state.get('party_members', [])])}
Enemies: {', '.join([enemy.get('name', 'Unknown') for enemy in combat_state.get('enemies', [])])}
Current Turn: {combat_state.get('current_turn', 0)}

Describe the immediate results of the combat action:
- What happens when the player takes their action
- How enemies respond
- The tactical situation and new options
- Any dramatic or exciting narrative elements
- Clear indication of what happens next in the combat

Focus on vivid, engaging combat descriptions that maintain tension and excitement."""

    return system_prompt, user_prompt


def generate_dialogue_prompt(game_state: dict, npc_name: str, player_dialogue: str) -> tuple[str, str]:
    """
    Generate a prompt for processing NPC dialogue interactions.

    Args:
        game_state (dict): Current game state for context
        npc_name (str): Name of the NPC being spoken to
        player_dialogue (str): Player's dialogue input

    Returns:
        tuple[str, str]: System prompt and user prompt for dialogue processing
    """
    system_prompt = ACTION_PROCESSING_SYSTEM_PROMPT

    user_prompt = f"""Process the player's dialogue with {npc_name}:

Player Says: "{player_dialogue}"

Current Context:
Location: {game_state.get('world_context', {}).get('current_location', 'Unknown')}
Player Character: {game_state.get('player_character', {}).get('name', 'Unknown')}

Respond as {npc_name} with:
- A natural, character-appropriate response
- Information, questions, or reactions based on the player's words
- Potential quest hooks or story advancement
- The NPC's personality and motivations coming through
- Clear indication of what the player can do next in the conversation

Keep the dialogue engaging and advance the story or relationship with the NPC."""

    return system_prompt, user_prompt
