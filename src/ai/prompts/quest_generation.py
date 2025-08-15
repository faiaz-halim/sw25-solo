from .system_prompts import QUEST_GENERATION_SYSTEM_PROMPT


def generate_quest_prompt(game_state: dict) -> tuple[str, str]:
    """
    Generate a prompt for creating a new quest based on game state.

    Args:
        game_state (dict): Current game state for context

    Returns:
        tuple[str, str]: System prompt and user prompt for quest generation
    """
    system_prompt = QUEST_GENERATION_SYSTEM_PROMPT

    user_prompt = f"""Create a new quest for the player based on the following game state:

Current Location: {game_state.get('world_context', {}).get('current_location', 'Unknown')}
World Description: {game_state.get('world_context', {}).get('world_description', 'Unknown')}
Player Level: {game_state.get('player_character', {}).get('level', 1) if game_state.get('player_character') else 1}
Active Quests: {len(game_state.get('active_quests', []))}
Party Size: {len(game_state.get('party_members', [])) + 1}

Create an engaging quest that fits the current campaign setting and player capabilities.

Include the following elements:

1. Quest Title: A compelling, descriptive name
2. Quest Hook: How the players learn about this quest
3. Objective: What needs to be accomplished (clear and actionable)
4. Challenges: What obstacles or enemies stand in the way
5. Rewards: What the players gain for completion (XP, items, story progression)
6. Complications: Optional twists or additional layers
7. Conclusion: How the quest ends and what happens next

Make the quest appropriate for the player's level and current story context.
Provide clear, actionable objectives with meaningful choices.

Format your response as follows:

QUEST TITLE: [Title]
QUEST HOOK: [How the players discover the quest]
OBJECTIVE: [What needs to be done]
CHALLENGES: [Obstacles and enemies]
REWARDS: [What they gain]
COMPLICATIONS: [Optional twists]
CONCLUSION: [How it ends]"""

    return system_prompt, user_prompt


def generate_side_quest_prompt(game_state: dict, location: str) -> tuple[str, str]:
    """
    Generate a prompt for creating a side quest for a specific location.

    Args:
        game_state (dict): Current game state for context
        location (str): Location where the side quest takes place

    Returns:
        tuple[str, str]: System prompt and user prompt for side quest generation
    """
    system_prompt = QUEST_GENERATION_SYSTEM_PROMPT

    user_prompt = f"""Create a side quest that takes place in {location} based on the following game state:

Current Location: {game_state.get('world_context', {}).get('current_location', 'Unknown')}
Player Level: {game_state.get('player_character', {}).get('level', 1) if game_state.get('player_character') else 1}
Party Size: {len(game_state.get('party_members', [])) + 1}

Create a self-contained side quest that can be completed relatively quickly but still feels meaningful.

Include:
- A clear problem or request from NPCs
- 2-3 specific objectives
- Appropriate challenges for the player's level
- Meaningful rewards
- A satisfying conclusion

Focus on local issues and characters that make the location feel more alive and important."""

    return system_prompt, user_prompt


def generate_quest_resolution_prompt(quest_title: str, player_actions: str, game_state: dict) -> tuple[str, str]:
    """
    Generate a prompt for resolving a quest based on player actions.

    Args:
        quest_title (str): Title of the quest being resolved
        player_actions (str): Description of what the player did
        game_state (dict): Current game state for context

    Returns:
        tuple[str, str]: System prompt and user prompt for quest resolution
    """
    system_prompt = QUEST_GENERATION_SYSTEM_PROMPT

    user_prompt = f"""Resolve the quest "{quest_title}" based on the player's actions:

Player Actions: {player_actions}

Current Game State:
Player Level: {game_state.get('player_character', {}).get('level', 1) if game_state.get('player_character') else 1}
Location: {game_state.get('world_context', {}).get('current_location', 'Unknown')}

Describe the outcome of the quest based on the player's approach. Include:
- How the quest concludes based on their actions
- What rewards they receive
- How the world changes as a result
- What new opportunities or story hooks emerge
- Any consequences of their choices

Provide a satisfying conclusion that acknowledges their specific approach to the quest."""

    return system_prompt, user_prompt
