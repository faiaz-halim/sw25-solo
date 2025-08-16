#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.ai.ai_gm import AIGameMaster
from src.ai.prompts import world_generation
import logging

# Set up logging to see debug output
logging.basicConfig(level=logging.DEBUG)

def debug_world_generation():
    print("Debugging world generation...")
    ai_gm = AIGameMaster()

    # Get the prompts
    system_prompt, user_prompt = world_generation.generate_world_prompt()
    print("=== SYSTEM PROMPT ===")
    print(system_prompt)
    print("\n=== USER PROMPT ===")
    print(user_prompt)

    try:
        print("\n=== CALLING LLM ===")
        response = ai_gm.client.call_llm(
            prompt=user_prompt,
            system_prompt=system_prompt,
            model="qwen/qwen3-30b-a3b:free",
            temperature=0.8
        )

        print("\n=== RAW LLM RESPONSE ===")
        import json
        print(json.dumps(response, indent=2))

        world_description = ai_gm.client.extract_text_response(response)
        print("\n=== EXTRACTED TEXT ===")
        print(repr(world_description))

        print("\n=== PARSED LINES ===")
        lines = world_description.strip().split('\n')
        for i, line in enumerate(lines):
            print(f"{i}: {repr(line)}")

        # Parse the structured response
        world_data = ai_gm._parse_world_response(world_description)
        print("\n=== PARSED WORLD DATA ===")
        print(json.dumps(world_data, indent=2))

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_world_generation()
