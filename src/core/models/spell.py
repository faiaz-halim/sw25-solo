from pydantic import BaseModel
from typing import List, Optional
from .attributes import Class


class Spell(BaseModel):
    """Spell data class with attributes based on Sword World 2.5 rules."""
    id: str
    name: str
    level: int  # Spell level
    casting_class: Class  # Which class can cast this spell
    mp_cost: int  # MP required to cast
    casting_time: str  # e.g., "1 action", "1 minute"
    range: str  # e.g., "Touch", "30 feet", "Sight"
    area: str  # e.g., "Target", "10-foot radius", "Cone"
    duration: str  # e.g., "Instantaneous", "1 minute", "Concentration"
    saving_throw: Optional[str] = None  # e.g., "Reflex", "Will", "Fortitude"
    spell_resistance: bool = False  # Whether spell resistance applies
    description: str  # Detailed description of the spell's effect
    components: List[str] = []  # e.g., ["V", "S", "M"]
    special_properties: List[str] = []  # e.g., ["Fire", "Lightning"]
