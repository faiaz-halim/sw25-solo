from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, Dict, Any, List
from .models import GameSession, GameAction, ConversationEntry
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class GameStateService:
    """Service to handle game state operations with PostgreSQL database."""

    def __init__(self, db: Session):
        self.db = db

    def create_game_session(self, session_id: str, game_state: Dict[str, Any]) -> GameSession:
        """
        Create a new game session in the database.

        Args:
            session_id (str): Unique session identifier
            game_state (Dict[str, Any]): Game state data

        Returns:
            GameSession: Created game session
        """
        try:
            game_session = GameSession.from_game_state(session_id, game_state)
            self.db.add(game_session)
            self.db.commit()
            self.db.refresh(game_session)
            logger.info(f"Created game session: {session_id}")
            return game_session
        except Exception as e:
            logger.error(f"Failed to create game session {session_id}: {str(e)}")
            self.db.rollback()
            raise

    def get_game_session(self, session_id: str) -> Optional[GameSession]:
        """
        Retrieve a game session from the database.

        Args:
            session_id (str): Session identifier

        Returns:
            Optional[GameSession]: Game session if found, None otherwise
        """
        try:
            return self.db.query(GameSession).filter(GameSession.id == session_id).first()
        except Exception as e:
            logger.error(f"Failed to retrieve game session {session_id}: {str(e)}")
            return None

    def update_game_session(self, session_id: str, game_state: Dict[str, Any]) -> bool:
        """
        Update an existing game session in the database.

        Args:
            session_id (str): Session identifier
            game_state (Dict[str, Any]): Updated game state data

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            game_session = self.db.query(GameSession).filter(GameSession.id == session_id).first()
            if not game_session:
                logger.warning(f"Game session {session_id} not found for update")
                return False

            # Update game state data
            game_session.player_name = game_state.get("player_character", {}).get("name", game_session.player_name)
            game_session.player_race = game_state.get("player_character", {}).get("race", game_session.player_race)
            game_session.player_class = game_state.get("player_character", {}).get("character_class", game_session.player_class)
            game_session.last_updated = datetime.now()
            game_session.is_active = True

            # Update all game data fields
            game_session.world_data = game_state.get("world_context", {})
            game_session.character_data = game_state.get("player_character", {})
            game_session.party_data = game_state.get("party_members", [])
            game_session.recruitable_characters_data = game_state.get("recruitable_characters", [])
            game_session.quests_data = game_state.get("active_quests", [])
            game_session.inventory_data = game_state.get("inventory", [])
            game_session.combat_state_data = game_state.get("combat_state", {})
            game_session.game_flags_data = game_state.get("game_flags", {})
            game_session.conversation_history_data = game_state.get("conversation_history", [])

            self.db.commit()
            self.db.refresh(game_session)
            logger.info(f"Updated game session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update game session {session_id}: {str(e)}")
            self.db.rollback()
            return False

    def save_game_action(self, session_id: str, action_type: str, action_content: str, response_content: str = None) -> bool:
        """
        Save a game action to the database.

        Args:
            session_id (str): Session identifier
            action_type (str): Type of action
            action_content (str): Action content
            response_content (str): Response content (optional)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            game_action = GameAction(
                session_id=session_id,
                action_type=action_type,
                action_content=action_content,
                response_content=response_content
            )
            self.db.add(game_action)
            self.db.commit()
            logger.info(f"Saved game action for session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save game action for session {session_id}: {str(e)}")
            self.db.rollback()
            return False

    def get_conversation_history(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session.

        Args:
            session_id (str): Session identifier
            limit (int): Maximum number of entries to return

        Returns:
            List[Dict[str, Any]]: Conversation history
        """
        try:
            entries = self.db.query(ConversationEntry)\
                .filter(ConversationEntry.session_id == session_id)\
                .order_by(desc(ConversationEntry.created_at))\
                .limit(limit)\
                .all()

            # Convert to the format expected by the frontend
            conversation_history = []
            for entry in reversed(entries):  # Reverse to get chronological order
                conversation_history.append({
                    "timestamp": entry.created_at.isoformat() if entry.created_at else datetime.now().isoformat(),
                    "type": entry.entry_type,
                    "content": entry.content
                })

            return conversation_history
        except Exception as e:
            logger.error(f"Failed to retrieve conversation history for session {session_id}: {str(e)}")
            return []

    def save_conversation_entry(self, session_id: str, entry_type: str, content: str) -> bool:
        """
        Save a conversation entry to the database.

        Args:
            session_id (str): Session identifier
            entry_type (str): Type of entry ('player' or 'narrative')
            content (str): Entry content

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conversation_entry = ConversationEntry(
                session_id=session_id,
                entry_type=entry_type,
                content=content
            )
            self.db.add(conversation_entry)
            self.db.commit()
            logger.info(f"Saved conversation entry for session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save conversation entry for session {session_id}: {str(e)}")
            self.db.rollback()
            return False

    def list_game_sessions(self) -> List[Dict[str, Any]]:
        """
        List all game sessions.

        Returns:
            List[Dict[str, Any]]: List of game sessions
        """
        try:
            sessions = self.db.query(GameSession)\
                .order_by(desc(GameSession.last_updated))\
                .all()

            return [session.to_dict() for session in sessions]
        except Exception as e:
            logger.error(f"Failed to list game sessions: {str(e)}")
            return []

    def delete_game_session(self, session_id: str) -> bool:
        """
        Delete a game session from the database.

        Args:
            session_id (str): Session identifier

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            game_session = self.db.query(GameSession).filter(GameSession.id == session_id).first()
            if not game_session:
                logger.warning(f"Game session {session_id} not found for deletion")
                return False

            self.db.delete(game_session)
            self.db.commit()
            logger.info(f"Deleted game session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete game session {session_id}: {str(e)}")
            self.db.rollback()
            return False


# Convenience functions for easy access
def create_game_session(db: Session, session_id: str, game_state: Dict[str, Any]) -> Optional[GameSession]:
    """Create a new game session."""
    service = GameStateService(db)
    return service.create_game_session(session_id, game_state)


def get_game_session(db: Session, session_id: str) -> Optional[GameSession]:
    """Get a game session."""
    service = GameStateService(db)
    return service.get_game_session(session_id)


def update_game_session(db: Session, session_id: str, game_state: Dict[str, Any]) -> bool:
    """Update a game session."""
    service = GameStateService(db)
    return service.update_game_session(session_id, game_state)


def save_game_action(db: Session, session_id: str, action_type: str, action_content: str, response_content: str = None) -> bool:
    """Save a game action."""
    service = GameStateService(db)
    return service.save_game_action(session_id, action_type, action_content, response_content)


def get_conversation_history(db: Session, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Get conversation history."""
    service = GameStateService(db)
    return service.get_conversation_history(session_id, limit)


def save_conversation_entry(db: Session, session_id: str, entry_type: str, content: str) -> bool:
    """Save a conversation entry."""
    service = GameStateService(db)
    return service.save_conversation_entry(session_id, entry_type, content)


def list_game_sessions(db: Session) -> List[Dict[str, Any]]:
    """List all game sessions."""
    service = GameStateService(db)
    return service.list_game_sessions()


def delete_game_session(db: Session, session_id: str) -> bool:
    """Delete a game session."""
    service = GameStateService(db)
    return service.delete_game_session(session_id)
