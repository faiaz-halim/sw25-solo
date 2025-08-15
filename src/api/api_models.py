from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
from src.core.models.attributes import Race, Class
from src.core.models.character import CharacterSheet
from src.core.models.quest import Quest
from src.core.models.item import Item


class NewGameRequest(BaseModel):
    """Request model for creating a new game."""
    player_name: str
    player_race: str
    player_class: str

    @validator('player_race')
    def validate_race(cls, v):
        if not isinstance(v, str):
            raise ValueError(f'Race must be a string, got {type(v)}')
        try:
            # Handle the specific enum values from the HTML
            race_mapping = {
                'HUMAN': Race.HUMAN,
                'ELF': Race.ELF,
                'DWARF': Race.DWARF,
                'GNOME': Race.GNOME,
                'HALFLING': Race.HALFLING,
                'HALF_ELF': Race.HALF_ELF,
                'HALF_DWARF': Race.HALF_DWARF
            }
            if v.upper() in race_mapping:
                return race_mapping[v.upper()]
            # Fallback to direct enum creation
            return Race(v.upper().replace('-', '_'))
        except (ValueError, AttributeError) as e:
            valid_races = [race.name for race in Race]
            raise ValueError(f'Invalid race: {v}. Valid races are: {valid_races}')

    @validator('player_class')
    def validate_class(cls, v):
        if not isinstance(v, str):
            raise ValueError(f'Class must be a string, got {type(v)}')
        try:
            # Handle the specific enum values from the HTML
            class_mapping = {
                'FIGHTER': Class.FIGHTER,
                'WIZARD': Class.WIZARD,
                'PRIEST': Class.PRIEST,
                'ROGUE': Class.ROGUE,
                'RANGER': Class.RANGER,
                'PALADIN': Class.PALADIN,
                'BARD': Class.BARD,
                'DRUID': Class.DRUID,
                'MONK': Class.MONK,
                'PSIONIC': Class.PSIONIC
            }
            if v.upper() in class_mapping:
                return class_mapping[v.upper()]
            # Fallback to direct enum creation
            return Class(v.upper().replace('-', '_'))
        except (ValueError, AttributeError) as e:
            valid_classes = [cls.name for cls in Class]
            raise ValueError(f'Invalid class: {v}. Valid classes are: {valid_classes}')


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
