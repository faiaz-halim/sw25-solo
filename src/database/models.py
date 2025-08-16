from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any
import json

Base = declarative_base()


class GameSession(Base):
    __tablename__ = 'game_sessions'

    id = Column(String, primary_key=True)
    player_name = Column(String, nullable=False)
    player_race = Column(String, nullable=False)
    player_class = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)

    # Game state data
    world_data = Column(JSON)
    character_data = Column(JSON)
    party_data = Column(JSON)
    recruitable_characters_data = Column(JSON)
    quests_data = Column(JSON)
    inventory_data = Column(JSON)
    combat_state_data = Column(JSON)
    game_flags_data = Column(JSON)
    conversation_history_data = Column(JSON)

    def to_dict(self) -> Dict[str, Any]:
        """Convert game session to dictionary for API response."""
        return {
            "session_id": self.id,
            "player_name": self.player_name,
            "player_race": self.player_race,
            "player_class": self.player_class,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "is_active": self.is_active,
            "world_data": self.world_data,
            "character_data": self.character_data,
            "party_data": self.party_data,
            "recruitable_characters_data": self.recruitable_characters_data,
            "quests_data": self.quests_data,
            "inventory_data": self.inventory_data,
            "combat_state_data": self.combat_state_data,
            "game_flags_data": self.game_flags_data,
            "conversation_history_data": self.conversation_history_data
        }

    @classmethod
    def from_game_state(cls, session_id: str, game_state: Dict[str, Any]) -> 'GameSession':
        """Create GameSession from game state dictionary."""
        # Handle datetime fields
        created_at_str = game_state.get("created_at")
        last_updated_str = game_state.get("last_updated")

        created_at = None
        last_updated = None

        if created_at_str:
            try:
                created_at = datetime.fromisoformat(created_at_str)
            except (ValueError, TypeError):
                created_at = datetime.now()
        else:
            created_at = datetime.now()

        if last_updated_str:
            try:
                last_updated = datetime.fromisoformat(last_updated_str)
            except (ValueError, TypeError):
                last_updated = datetime.now()
        else:
            last_updated = datetime.now()

        return cls(
            id=session_id,
            player_name=game_state.get("player_character", {}).get("name", "Unknown"),
            player_race=game_state.get("player_character", {}).get("race", "HUMAN"),
            player_class=game_state.get("player_character", {}).get("character_class", "FIGHTER"),
            created_at=created_at,
            last_updated=last_updated,
            world_data=game_state.get("world_context", {}),
            character_data=game_state.get("player_character", {}),
            party_data=game_state.get("party_members", []),
            recruitable_characters_data=game_state.get("recruitable_characters", []),
            quests_data=game_state.get("active_quests", []),
            inventory_data=game_state.get("inventory", []),
            combat_state_data=game_state.get("combat_state", {}),
            game_flags_data=game_state.get("game_flags", {}),
            conversation_history_data=game_state.get("conversation_history", [])
        )


class GameAction(Base):
    __tablename__ = 'game_actions'

    id = Column(Integer, primary_key=True)
    session_id = Column(String, ForeignKey('game_sessions.id'), nullable=False)
    action_type = Column(String, nullable=False)
    action_content = Column(Text, nullable=False)
    response_content = Column(Text)
    created_at = Column(DateTime, default=func.now())

    # Relationship
    session = relationship("GameSession", back_populates="actions")

    def to_dict(self) -> Dict[str, Any]:
        """Convert game action to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "action_type": self.action_type,
            "action_content": self.action_content,
            "response_content": self.response_content,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# Add relationship to GameSession
GameSession.actions = relationship("GameAction", back_populates="session", cascade="all, delete-orphan")


class ConversationEntry(Base):
    __tablename__ = 'conversation_entries'

    id = Column(Integer, primary_key=True)
    session_id = Column(String, ForeignKey('game_sessions.id'), nullable=False)
    entry_type = Column(String, nullable=False)  # 'player' or 'narrative'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Relationship
    session = relationship("GameSession", back_populates="conversation_entries")


# Add relationship to GameSession
GameSession.conversation_entries = relationship("ConversationEntry", back_populates="session", cascade="all, delete-orphan")
