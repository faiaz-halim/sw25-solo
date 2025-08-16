#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from src.ai.ai_gm import AIGameMaster

def test_world_generation():
    print("Testing world generation...")
    ai_gm = AIGameMaster()

    try:
        world_data = ai_gm.generate_initial_world()
        print("World data generated successfully:")
        print(f"Region name: '{world_data.get('region_name', 'NOT FOUND')}'")
        print(f"Region description: '{world_data.get('region_description', 'NOT FOUND')}'")
        print(f"Settlements: {world_data.get('settlements', 'NOT FOUND')}")
        print(f"Central conflict: '{world_data.get('central_conflict', 'NOT FOUND')}'")
        print("\nFull world data:")
        for key, value in world_data.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"Error generating world: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_world_generation()
