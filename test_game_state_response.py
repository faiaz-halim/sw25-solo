#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.api.api_models import GameStateResponse
from src.core.models.character import CharacterSheet
from src.core.models.attributes import Race, Class

def test_game_state_response():
    print("Testing GameStateResponse creation...")

    # Create a simple character for testing
    character = CharacterSheet(
        id="test_123",
        name="Test Character",
        race=Race.HUMAN,
        character_class=Class.FIGHTER,
        level=1,
        experience_points=0,
        strength=10,
        dexterity=10,
        vitality=10,
        intelligence=10,
        spirit=10,
        hit_points=10,
        max_hit_points=10,
        magic_points=0,
        max_magic_points=0,
        defense=10,
        attack_bonus=1,
        skills={},
        spells=[],
        inventory=[],
        equipped_weapon=None,
        equipped_armor=None,
        equipped_accessories=[],
        backstory="Test backstory",
        alignment="Neutral"
    )

    # Test world context data
    world_context = {
        "current_location": "The Borderlands",
        "world_description": "A frontier region where civilization meets the wild unknown. Ancient ruins dot the landscape alongside small farming villages and trading posts.",
        "time_of_day": "day",
        "weather": "clear"
    }

    print("Creating GameStateResponse...")
    try:
        response = GameStateResponse(
            session_id="test_session_123",
            player_character=character,
            party_members=[],
            active_quests=[],
            world_context=world_context,
            inventory=[],
            combat_state=None,
            narrative="Test narrative",
            new_options=["Option 1", "Option 2"],
            game_flags={}
        )

        print("GameStateResponse created successfully!")
        print(f"World context in response: {response.world_context}")
        print(f"Current location: {response.world_context.get('current_location', 'NOT FOUND')}")
        print(f"World description: {response.world_context.get('world_description', 'NOT FOUND')}")

        # Test JSON serialization
        print("\nJSON serialization test:")
        json_data = response.model_dump()
        print(f"World context in JSON: {json_data['world_context']}")

    except Exception as e:
        print(f"Error creating GameStateResponse: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_game_state_response()
