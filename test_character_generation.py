#!/usr/bin/env python3
"""
Test script to demonstrate character generation and show actual generated content.
"""

import sys
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from src.core.engine.character_creation import create_new_character, roll_on_history_table, roll_on_adventure_reason_table
from src.ai.ai_gm import AIGameMaster
from src.core.models.attributes import Race, Class

def main():
    print("=== Sword World 2.5 AI GM - Character Generation Test ===\n")

    # Test character creation with random rolls
    print("1. Creating character with random background...")
    character = create_new_character(
        name="Test Adventurer",
        race=Race.HUMAN,
        character_class=Class.FIGHTER
    )

    print(f"Character: {character.name}")
    print(f"Race: {character.race}")
    print(f"Class: {character.character_class}")
    print(f"Attributes: STR={character.strength}, DEX={character.dexterity}, VIT={character.vitality}, INT={character.intelligence}, SPI={character.spirit}")
    print(f"HP: {character.hit_points}/{character.max_hit_points}")
    print(f"MP: {character.magic_points}/{character.max_magic_points}")
    print(f"Defense: {character.defense}")
    print(f"Attack Bonus: {character.attack_bonus}")
    print("\nSkills:")
    for skill, level in character.skills.items():
        print(f"  {skill}: {level}")

    print(f"\nInitial Backstory (from tables):")
    print(f"  {character.backstory}")

    # Test AI-generated detailed backstory
    print("\n2. Generating AI-enhanced backstory...")
    try:
        ai_gm = AIGameMaster()
    except ValueError as e:
        print(f"AI Game Master initialization failed: {e}")
        print("This is expected if no API key is configured.")
        print("Showing fallback content instead...")

        # Show fallback content directly
        print(f"\nFallback Backstory:")
        print("-" * 30)
        fallback_details = {
            "backstory": "A Human Fighter who has chosen the path of adventure for reasons known only to them.",
            "personality_traits": [
                "Adaptable to new situations",
                "Curious about the world",
                "Determined to succeed",
                "Loyal to companions"
            ]
        }
        print(fallback_details["backstory"])
        print("-" * 30)

        print(f"\nFallback Personality Traits:")
        for trait in fallback_details["personality_traits"]:
            print(f"  - {trait}")

        # Test world generation with fallback
        print("\n3. Generating game world (fallback)...")
        fallback_world = {
            "region_name": "The Borderlands",
            "region_description": "A frontier region where civilization meets the wild unknown. Ancient ruins dot the landscape alongside small farming villages and trading posts.",
            "central_conflict": "Strange creatures have been sighted near the Oldwood, and trade routes are becoming dangerous",
            "settlements": [
                "Millhaven: A small farming village known for its grain mills",
                "Trader's Cross: A bustling trade post at the crossroads of several routes",
                "Old Keep: A ruined fortress that serves as a landmark and occasional shelter"
            ],
            "geographic_features": [
                "The Millhaven River: A swift-flowing river that powers the village mills",
                "The Oldwood: A dense forest rumored to be haunted",
                "The Border Hills: Rolling hills that mark the edge of civilized lands"
            ],
            "factions": [
                "The Millhaven Council: Local village leaders focused on maintaining order",
                "The Trader's Guild: Merchants interested in keeping trade routes safe",
                "The Rangers: Woodsmen who know the wilderness and track the strange creatures"
            ],
            "adventure_hooks": [
                "Investigate the strange creature sightings near Oldwood",
                "Help escort a valuable trade caravan through dangerous territory",
                "Explore the ancient ruins of Old Keep for lost treasures",
                "Resolve a dispute between two farming families over water rights"
            ]
        }

        print(f"\nFallback World:")
        print("-" * 30)
        print(f"Region: {fallback_world['region_name']}")
        print(f"Description: {fallback_world['region_description']}")
        print(f"Central Conflict: {fallback_world['central_conflict']}")

        print("\nKey Settlements:")
        for settlement in fallback_world['settlements']:
            print(f"  - {settlement}")

        print("\nGeographic Features:")
        for feature in fallback_world['geographic_features']:
            print(f"  - {feature}")

        print("\nLocal Factions:")
        for faction in fallback_world['factions']:
            print(f"  - {faction}")

        print("\nAdventure Hooks:")
        for i, hook in enumerate(fallback_world['adventure_hooks'], 1):
            print(f"  {i}. {hook}")

        print("\n=== Test Complete ===")
        return

    history_elements = {
        "history": character.backstory,
        "adventure_reason": "Seeking fortune and adventure"
    }

    try:
        character_details = ai_gm.generate_player_character_details(
            Race.HUMAN,
            Class.FIGHTER,
            history_elements
        )

        print(f"\nAI-Generated Detailed Backstory:")
        print("-" * 50)
        print(character_details["backstory"])
        print("-" * 50)

        print(f"\nPersonality Traits:")
        for trait in character_details["personality_traits"]:
            print(f"  - {trait}")

    except Exception as e:
        print(f"AI generation failed: {e}")
        print("Using fallback content...")

        # Show what the fallback would look like
        fallback_details = ai_gm._get_fallback_character_details(Race.HUMAN, Class.FIGHTER)
        print(f"\nFallback Backstory:")
        print("-" * 30)
        print(fallback_details["backstory"])
        print("-" * 30)

        print(f"\nFallback Personality Traits:")
        for trait in fallback_details["personality_traits"]:
            print(f"  - {trait}")

    # Test world generation
    print("\n3. Generating game world...")
    try:
        world_data = ai_gm.generate_initial_world()
        print(f"\nGenerated World:")
        print("-" * 30)
        print(f"Region: {world_data.get('region_name', 'Unknown')}")
        print(f"Description: {world_data.get('region_description', 'No description')}")
        print(f"Central Conflict: {world_data.get('central_conflict', 'No conflict')}")

        if world_data.get('settlements'):
            print("\nKey Settlements:")
            for settlement in world_data['settlements']:
                print(f"  - {settlement}")

        if world_data.get('geographic_features'):
            print("\nGeographic Features:")
            for feature in world_data['geographic_features']:
                print(f"  - {feature}")

        if world_data.get('factions'):
            print("\nLocal Factions:")
            for faction in world_data['factions']:
                print(f"  - {faction}")

        if world_data.get('adventure_hooks'):
            print("\nAdventure Hooks:")
            for i, hook in enumerate(world_data['adventure_hooks'], 1):
                print(f"  {i}. {hook}")

    except Exception as e:
        print(f"World generation failed: {e}")

        # Show fallback world
        fallback_world = ai_gm._get_fallback_world()
        print(f"\nFallback World:")
        print("-" * 30)
        print(f"Region: {fallback_world['region_name']}")
        print(f"Description: {fallback_world['region_description']}")
        print(f"Central Conflict: {fallback_world['central_conflict']}")

    print("\n=== Test Complete ===")

if __name__ == "__main__":
    # Add src to Python path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    main()
