from .openrouter_client import OpenRouterClient
from .prompts import (
    world_generation,
    character_generation,
    quest_generation,
    action_processing,
    npc_interaction,
    system_prompts
)
from ..core.models.character import CharacterSheet
from ..core.models.attributes import Race, Class
from ..core.engine.character_creation import create_new_character
from typing import Dict, List, Optional
import json
import logging

logger = logging.getLogger(__name__)


class AIGameMaster:
    """Main AI Game Master class that orchestrates all AI-driven game logic."""

    def __init__(self, api_key: str = None):
        """
        Initialize the AI Game Master.

        Args:
            api_key (str): OpenRouter API key. If not provided, loaded from environment.
        """
        self.client = OpenRouterClient(api_key)
        logger.info("AI Game Master initialized")

    def generate_initial_world(self) -> Dict:
        """
        Generate the initial game world using AI.

        Returns:
            Dict: Generated world description and key elements
        """
        logger.info("Generating initial world...")

        system_prompt, user_prompt = world_generation.generate_world_prompt()

        try:
            response = self.client.call_llm(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=1500,
                temperature=0.8
            )

            world_description = self.client.extract_text_response(response)

            # Parse the structured response
            world_data = self._parse_world_response(world_description)

            logger.info("Initial world generation complete")
            return world_data

        except Exception as e:
            logger.error(f"Failed to generate initial world: {str(e)}")
            # Return a fallback world
            return self._get_fallback_world()

    def _parse_world_response(self, response_text: str) -> Dict:
        """
        Parse the world generation response into structured data.

        Args:
            response_text (str): Raw AI response text

        Returns:
            Dict: Parsed world data
        """
        # Simple parsing for now - in a real implementation, this would be more sophisticated
        lines = response_text.strip().split('\n')
        world_data = {
            "region_name": "",
            "region_description": "",
            "settlements": [],
            "geographic_features": [],
            "central_conflict": "",
            "factions": [],
            "adventure_hooks": []
        }

        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("REGION NAME:"):
                world_data["region_name"] = line.replace("REGION NAME:", "").strip()
                current_section = "region_name"
            elif line.startswith("REGION DESCRIPTION:"):
                current_section = "region_description"
            elif line.startswith("KEY SETTLEMENTS:"):
                current_section = "settlements"
            elif line.startswith("GEOGRAPHIC FEATURES:"):
                current_section = "geographic_features"
            elif line.startswith("CENTRAL CONFLICT:"):
                world_data["central_conflict"] = line.replace("CENTRAL CONFLICT:", "").strip()
                current_section = "central_conflict"
            elif line.startswith("LOCAL FACTIONS:"):
                current_section = "factions"
            elif line.startswith("ADVENTURE HOOKS:"):
                current_section = "adventure_hooks"
            elif line.startswith("- ") and current_section in ["settlements", "geographic_features", "factions"]:
                world_data[current_section].append(line[2:].strip())
            elif line.startswith(("-", "1.", "2.", "3.", "4.")) and current_section == "adventure_hooks":
                # Remove numbering and add to hooks
                hook = line.split(".", 1)[1] if "." in line[:2] else line[2:]
                world_data["adventure_hooks"].append(hook.strip())
            elif current_section == "region_description" and line:
                if world_data["region_description"]:
                    world_data["region_description"] += " " + line
                else:
                    world_data["region_description"] = line

        return world_data

    def _get_fallback_world(self) -> Dict:
        """Provide a fallback world in case AI generation fails."""
        return {
            "region_name": "The Borderlands",
            "region_description": "A frontier region where civilization meets the wild unknown. Ancient ruins dot the landscape alongside small farming villages and trading posts.",
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
            "central_conflict": "Strange creatures have been sighted near the Oldwood, and trade routes are becoming dangerous",
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

    def generate_player_character_details(self, race: Race, character_class: Class, history_elements: Dict) -> Dict:
        """
        Generate detailed character background using AI.

        Args:
            race (Race): Character's race
            character_class (Class): Character's class
            history_elements (Dict): Background elements from history tables

        Returns:
            Dict: Generated character details including backstory and personality
        """
        logger.info(f"Generating character details for {race.value} {character_class.value}...")

        # Generate backstory
        system_prompt, user_prompt = character_generation.generate_backstory_prompt(
            race, character_class, history_elements
        )

        try:
            response = self.client.call_llm(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=800,
                temperature=0.7
            )

            backstory = self.client.extract_text_response(response)

            # Generate personality traits
            system_prompt, user_prompt = character_generation.generate_personality_prompt(
                race, character_class, backstory
            )

            response = self.client.call_llm(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=600,
                temperature=0.6
            )

            personality_text = self.client.extract_text_response(response)
            personality_traits = self._parse_personality_response(personality_text)

            logger.info("Character generation complete")
            return {
                "backstory": backstory,
                "personality_traits": personality_traits,
                "appearance": ""  # Could generate appearance too
            }

        except Exception as e:
            logger.error(f"Failed to generate character details: {str(e)}")
            return self._get_fallback_character_details(race, character_class)

    def _parse_personality_response(self, response_text: str) -> List[str]:
        """Parse personality traits from AI response."""
        traits = []
        lines = response_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith("-") or ":" in line):
                # Clean up the trait description
                trait = line.split(":", 1)[1] if ":" in line else line[1:]
                traits.append(trait.strip())
        return traits

    def _get_fallback_character_details(self, race: Race, character_class: Class) -> Dict:
        """Provide fallback character details."""
        return {
            "backstory": f"A {race.value} {character_class.value} who has chosen the path of adventure for reasons known only to them.",
            "personality_traits": [
                "Adaptable to new situations",
                "Curious about the world",
                "Determined to succeed",
                "Loyal to companions"
            ],
            "appearance": "A typical adventurer ready for the road ahead."
        }

    def generate_recruitable_npcs(self, count: int = 3) -> List[Dict]:
        """
        Generate recruitable NPC characters using AI.

        Args:
            count (int): Number of NPCs to generate

        Returns:
            List[Dict]: List of generated NPC character data
        """
        logger.info(f"Generating {count} recruitable NPCs...")

        npcs = []
        for i in range(count):
            # Simple template for now - in a real implementation, this would be more detailed
            npc_template = {
                "name": f"NPC_{i+1}",
                "race": "Human",
                "role": "Adventurer",
                "location": "Starting Village",
                "relationship": "neutral"
            }

            try:
                system_prompt, user_prompt = npc_interaction.generate_npc_personality_prompt(npc_template)

                response = self.client.call_llm(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    max_tokens=600,
                    temperature=0.7
                )

                personality_text = self.client.extract_text_response(response)
                # In a real implementation, this would parse the personality details

                npcs.append({
                    "id": f"npc_{i+1}",
                    "name": f"Recruitable Character {i+1}",
                    "personality": personality_text,
                    " recruitable": True
                })

            except Exception as e:
                logger.error(f"Failed to generate NPC {i+1}: {str(e)}")
                npcs.append({
                    "id": f"npc_{i+1}",
                    "name": f"Fallback NPC {i+1}",
                    "personality": "A reliable companion ready for adventure.",
                    "recruitable": True
                })

        logger.info("NPC generation complete")
        return npcs

    def process_player_action(self, game_state: Dict, player_input: str) -> Dict:
        """
        Process a player's action and generate appropriate narrative response.

        Args:
            game_state (Dict): Current game state
            player_input (str): Player's action input

        Returns:
            Dict: Processing results including narrative response and state changes
        """
        logger.info(f"Processing player action: {player_input}")

        system_prompt, user_prompt = action_processing.generate_action_prompt(game_state, player_input)

        try:
            response = self.client.call_llm(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=600,
                temperature=0.7
            )

            narrative_response = self.client.extract_text_response(response)

            logger.info("Player action processed successfully")
            return {
                "narrative": narrative_response,
                "state_changes": {},  # In a real implementation, this would track state changes
                "new_options": self._extract_options_from_response(narrative_response)
            }

        except Exception as e:
            logger.error(f"Failed to process player action: {str(e)}")
            return {
                "narrative": "You consider your options carefully.",
                "state_changes": {},
                "new_options": ["Look around", "Check inventory", "Rest"]
            }

    def _extract_options_from_response(self, response_text: str) -> List[str]:
        """Extract action options from AI response."""
        # Simple extraction - in a real implementation, this would be more sophisticated
        options = []
        if "you could" in response_text.lower():
            options.append("Consider the suggestion")
        if "alternatively" in response_text.lower():
            options.append("Choose alternative path")
        if "another option" in response_text.lower():
            options.append("Explore other choices")

        # Add some default options
        if not options:
            options = ["Continue forward", "Look around", "Check inventory"]

        return options[:3]  # Limit to 3 options

    def generate_new_quest(self, game_state: Dict) -> Dict:
        """
        Generate a new quest based on current game state.

        Args:
            game_state (Dict): Current game state for context

        Returns:
            Dict: Generated quest data
        """
        logger.info("Generating new quest...")

        system_prompt, user_prompt = quest_generation.generate_quest_prompt(game_state)

        try:
            response = self.client.call_llm(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=800,
                temperature=0.7
            )

            quest_text = self.client.extract_text_response(response)
            quest_data = self._parse_quest_response(quest_text)

            logger.info("Quest generation complete")
            return quest_data

        except Exception as e:
            logger.error(f"Failed to generate quest: {str(e)}")
            return self._get_fallback_quest()

    def _parse_quest_response(self, response_text: str) -> Dict:
        """Parse quest generation response into structured data."""
        lines = response_text.strip().split('\n')
        quest_data = {
            "title": "Mysterious Quest",
            "hook": "",
            "objective": "",
            "challenges": "",
            "rewards": "",
            "complications": "",
            "conclusion": ""
        }

        current_field = None
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("QUEST TITLE:"):
                quest_data["title"] = line.replace("QUEST TITLE:", "").strip()
            elif line.startswith("QUEST HOOK:"):
                current_field = "hook"
                quest_data[current_field] = line.replace("QUEST HOOK:", "").strip()
            elif line.startswith("OBJECTIVE:"):
                current_field = "objective"
                quest_data[current_field] = line.replace("OBJECTIVE:", "").strip()
            elif line.startswith("CHALLENGES:"):
                current_field = "challenges"
                quest_data[current_field] = line.replace("CHALLENGES:", "").strip()
            elif line.startswith("REWARDS:"):
                current_field = "rewards"
                quest_data[current_field] = line.replace("REWARDS:", "").strip()
            elif line.startswith("COMPLICATIONS:"):
                current_field = "complications"
                quest_data[current_field] = line.replace("COMPLICATIONS:", "").strip()
            elif line.startswith("CONCLUSION:"):
                current_field = "conclusion"
                quest_data[current_field] = line.replace("CONCLUSION:", "").strip()
            elif current_field and line:
                quest_data[current_field] += " " + line

        return quest_data

    def _get_fallback_quest(self) -> Dict:
        """Provide a fallback quest."""
        return {
            "title": "The Missing Merchant",
            "hook": "A local merchant asks for help finding their missing supply caravan",
            "objective": "Locate the missing caravan and discover what happened to it",
            "challenges": "Bandits, wilderness dangers, and mysterious circumstances",
            "rewards": "Gold, experience, and the merchant's gratitude",
            "complications": "The caravan may have been attacked by bandits or led astray",
            "conclusion": "The caravan is found and the mystery is solved"
        }


# Convenience functions for easy access
def generate_initial_world() -> Dict:
    """Generate initial world using the AI Game Master."""
    gm = AIGameMaster()
    return gm.generate_initial_world()


def generate_player_character_details(race: Race, character_class: Class, history_elements: Dict) -> Dict:
    """Generate player character details using the AI Game Master."""
    gm = AIGameMaster()
    return gm.generate_player_character_details(race, character_class, history_elements)


def generate_recruitable_npcs(count: int = 3) -> List[Dict]:
    """Generate recruitable NPCs using the AI Game Master."""
    gm = AIGameMaster()
    return gm.generate_recruitable_npcs(count)


def process_player_action(game_state: Dict, player_input: str) -> Dict:
    """Process player action using the AI Game Master."""
    gm = AIGameMaster()
    return gm.process_player_action(game_state, player_input)


def generate_new_quest(game_state: Dict) -> Dict:
    """Generate a new quest using the AI Game Master."""
    gm = AIGameMaster()
    return gm.generate_new_quest(game_state)
