from .models.character import CharacterSheet
from .models.monster import Monster
from .models.quest import Quest
from .models.item import Item
from typing import List, Dict, Optional
import json
import os
from datetime import datetime


class GameState:
    """Manages the complete game state including characters, quests, and world context."""

    def __init__(self, session_id: str = None):
        self.session_id = session_id or f"session_{int(datetime.now().timestamp())}"
        self.player_character: Optional[CharacterSheet] = None
        self.party_members: List[CharacterSheet] = []
        self.recruitable_characters: List[CharacterSheet] = []  # Characters available for recruitment
        self.active_quests: List[Quest] = []
        self.completed_quests: List[Quest] = []
        self.world_context: Dict = {
            "current_location": "Starting Village",
            "world_description": "A small village at the edge of civilization",
            "time_of_day": "day",
            "weather": "clear"
        }
        self.inventory: List[Item] = []
        self.combat_state: Optional[Dict] = None
        self.game_flags: Dict[str, bool] = {}  # For tracking story flags
        self.conversation_history: List[Dict] = []  # Track conversation between player and AI GM
        self.created_at = datetime.now()
        self.last_updated = datetime.now()

    def add_party_member(self, character: CharacterSheet):
        """Add a character to the party."""
        self.party_members.append(character)

    def remove_party_member(self, character_id: str) -> bool:
        """Remove a character from the party. Returns True if successful."""
        for i, character in enumerate(self.party_members):
            if character.id == character_id:
                self.party_members.pop(i)
                return True
        return False

    def add_quest(self, quest: Quest):
        """Add a new quest to the active quests list."""
        self.active_quests.append(quest)

    def complete_quest(self, quest_id: str) -> bool:
        """Mark a quest as completed. Returns True if successful."""
        for i, quest in enumerate(self.active_quests):
            if quest.id == quest_id:
                completed_quest = self.active_quests.pop(i)
                completed_quest.update_status(completed_quest.status.__class__.COMPLETED)
                self.completed_quests.append(completed_quest)
                return True
        return False

    def add_item_to_inventory(self, item: Item):
        """Add an item to the party's inventory."""
        self.inventory.append(item)

    def remove_item_from_inventory(self, item_id: str) -> bool:
        """Remove an item from the party's inventory. Returns True if successful."""
        for i, item in enumerate(self.inventory):
            if item.id == item_id:
                self.inventory.pop(i)
                return True
        return False

    def update_world_context(self, **kwargs):
        """Update world context variables."""
        self.world_context.update(kwargs)
        self.last_updated = datetime.now()

    def set_flag(self, flag_name: str, value: bool = True):
        """Set a game flag."""
        self.game_flags[flag_name] = value
        self.last_updated = datetime.now()

    def get_flag(self, flag_name: str) -> bool:
        """Get a game flag value."""
        return self.game_flags.get(flag_name, False)

    def start_combat(self, enemies: List[Monster]):
        """Initialize combat state."""
        self.combat_state = {
            "is_active": True,
            "enemies": enemies,
            "turn_order": [self.player_character] + self.party_members + enemies,
            "current_turn": 0
        }
        self.last_updated = datetime.now()

    def end_combat(self):
        """End combat state."""
        self.combat_state = None
        self.last_updated = datetime.now()

    def to_dict(self) -> Dict:
        """Convert game state to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "player_character": self.player_character.model_dump() if self.player_character else None,
            "party_members": [char.model_dump() for char in self.party_members],
            "recruitable_characters": [char.model_dump() for char in self.recruitable_characters],
            "active_quests": [quest.model_dump() for quest in self.active_quests],
            "completed_quests": [quest.model_dump() for quest in self.completed_quests],
            "world_context": self.world_context,
            "inventory": [item.model_dump() for item in self.inventory],
            "combat_state": self.combat_state,  # This would need special handling for complex objects
            "game_flags": self.game_flags,
            "conversation_history": self.conversation_history,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'GameState':
        """Create game state from dictionary."""
        state = cls(data["session_id"])

        # This would need proper deserialization of complex objects
        # For now, we'll just restore the basic structure
        state.world_context = data.get("world_context", {})
        state.game_flags = data.get("game_flags", {})
        state.conversation_history = data.get("conversation_history", [])

        # Handle datetime fields safely
        try:
            created_at_str = data.get("created_at")
            if created_at_str:
                try:
                    state.created_at = datetime.fromisoformat(created_at_str)
                except (ValueError, TypeError):
                    state.created_at = datetime.now()
            else:
                state.created_at = datetime.now()
        except Exception:
            state.created_at = datetime.now()

        try:
            last_updated_str = data.get("last_updated")
            if last_updated_str:
                try:
                    state.last_updated = datetime.fromisoformat(last_updated_str)
                except (ValueError, TypeError):
                    state.last_updated = datetime.now()
            else:
                state.last_updated = datetime.now()
        except Exception:
            state.last_updated = datetime.now()

        return state

    def save_to_file(self, filepath: str = None) -> str:
        """
        Save game state to a JSON file.

        Args:
            filepath (str): Path to save file. If None, uses session_id.

        Returns:
            str: Path to the saved file
        """
        if filepath is None:
            filepath = f"saves/{self.session_id}.json"

        # Ensure saves directory exists
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else "saves", exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

        return filepath

    @classmethod
    def load_from_file(cls, filepath: str) -> 'GameState':
        """
        Load game state from a JSON file.

        Args:
            filepath (str): Path to the save file.

        Returns:
            GameState: Loaded game state
        """
        with open(filepath, 'r') as f:
            data = json.load(f)

        return cls.from_dict(data)


def save_game(state: GameState, filepath: str = None) -> str:
    """
    Save game state to file.

    Args:
        state (GameState): Game state to save
        filepath (str): Path to save file

    Returns:
        str: Path to the saved file
    """
    return state.save_to_file(filepath)


def load_game(filepath: str) -> GameState:
    """
    Load game state from file.

    Args:
        filepath (str): Path to the save file

    Returns:
        GameState: Loaded game state
    """
    return GameState.load_from_file(filepath)
