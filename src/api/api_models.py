from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from ..core.models.attributes import Race, Class
from ..core.models.character import CharacterSheet
from ..core.models.quest import Quest
from ..core.models.item import Item


class NewGameRequest(BaseModel):
    """Request model for creating a new game."""
    player_name: str
    player_race: Race
    player_class: Class


class ActionRequest(BaseModel):
    """Request model for player actions."""
    action_type: str  # e.g., "text", "attack", "use_item"
    value: str  # The actual action content


class GameStateResponse(BaseModel):
    """Response model for game state."""
    session_id: str
    player_character: Optional[CharacterSheet] = None
    party_members: List[CharacterSheet] = []
    active_quests: List[Quest] = []
    world_context: Dict[str, Any] = {}
    inventory: List[Item] = []
    combat_state: Optional[Dict[str, Any]] = None
    narrative: str = ""  # Current narrative text from the GM
    new_options: List[str] = []  # New action options from the GM
    game_flags: Dict[str, bool] = {}


class GameCreationResponse(BaseModel):
    """Response model for game creation."""
    session_id: str
    initial_state: GameStateResponse
    message: str = "Game created successfully"


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str
    message: str
    details: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    message: str
