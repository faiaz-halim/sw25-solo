from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict
from src.api.api_models import (
    NewGameRequest,
    ActionRequest,
    GameStateResponse,
    GameCreationResponse
)
from src.core.game_state import GameState
from src.core.engine.character_creation import create_new_character
from src.core.models.attributes import Race, Class
from src.ai.ai_gm import AIGameMaster
from src.database.database import get_db
from src.database.game_state_service import (
    create_game_session,
    get_game_session,
    update_game_session,
    save_game_action,
    get_conversation_history,
    save_conversation_entry
)
from sqlalchemy.orm import Session
import logging
import uuid
from datetime import datetime
import random

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.post("/new", response_model=GameCreationResponse)
async def create_new_game(request: NewGameRequest, db: Session = Depends(get_db)):
    """
    Create a new game session.

    Args:
        request (NewGameRequest): Player's initial choices
        db (Session): Database session

    Returns:
        GameCreationResponse: Initial game state and session information
    """
    try:
        logger.info(f"Creating new game for player: {request.player_name}")

        # Initialize AI Game Master
        ai_gm = AIGameMaster()

        # Generate initial world
        world_data = ai_gm.generate_initial_world()

        # Create player character with backstory choices
        player_character = create_new_character(
            name=request.player_name,
            race=request.player_race,  # This is now a Race enum
            character_class=request.player_class,  # This is now a Class enum
            history_choice=request.history_choice,
            adventure_reason_choice=request.adventure_reason_choice
        )

        # Generate character details using AI
        history_elements = {
            "history": player_character.backstory,
            "adventure_reason": "Seeking fortune and adventure"
        }
        character_details = ai_gm.generate_player_character_details(
            request.player_race,
            request.player_class,
            history_elements
        )

        # Update character with AI-generated details
        player_character.backstory = character_details["backstory"]

        # Create new game state
        session_id = str(uuid.uuid4())
        game_state = GameState(session_id=session_id)
        game_state.player_character = player_character
        game_state.world_context = {
            "current_location": world_data.get("region_name", "Starting Region"),
            "world_description": world_data.get("region_description", "A mysterious land"),
            "time_of_day": "day",
            "weather": "clear"
        }

        # Generate initial recruitable NPCs
        recruitable_npcs = ai_gm.generate_recruitable_npcs(count=3)

        # Convert NPC data to CharacterSheet objects
        for i, npc_data in enumerate(recruitable_npcs):
            # Create random race and class for NPC
            import random
            npc_race = random.choice(list(Race))
            npc_class = random.choice(list(Class))

            # Generate NPC character
            npc_character = create_new_character(
                name=npc_data.get("name", f"NPC_{i+1}"),
                race=npc_race,
                character_class=npc_class
            )

            # Add to recruitable list (not yet in party)
            game_state.recruitable_characters.append(npc_character)

        # Add initial narrative from AI
        initial_prompt = f"Welcome {request.player_name}, a {request.player_race.value} {request.player_class.value}. {character_details['backstory'][:100]}... You find yourself in {world_data.get('region_name', 'the starting region')}."
        action_result = ai_gm.process_player_action(
            game_state.to_dict(),
            f"Look around {world_data.get('region_name', 'the area')}"
        )

        # Add initial conversation to history
        initial_conversation = {
            "timestamp": datetime.now().isoformat(),
            "type": "narrative",
            "content": action_result["narrative"]
        }
        game_state.conversation_history.append(initial_conversation)

        # Save to database
        game_state_dict = game_state.to_dict()
        create_game_session(db, session_id, game_state_dict)

        # Save initial conversation entries
        save_conversation_entry(db, session_id, "narrative", action_result["narrative"])

        # Create response
        game_state_response = GameStateResponse(
            session_id=session_id,
            player_character=player_character,
            party_members=game_state.party_members,
            recruitable_characters=game_state.recruitable_characters,
            active_quests=game_state.active_quests,
            world_context=game_state.world_context,
            inventory=game_state.inventory,
            combat_state=game_state.combat_state,
            narrative=action_result["narrative"],
            new_options=action_result["new_options"],
            game_flags=game_state.game_flags,
            conversation_history=game_state.conversation_history
        )

        logger.info(f"New game created successfully with session ID: {session_id}")

        return GameCreationResponse(
            session_id=session_id,
            initial_state=game_state_response,
            message="Game created successfully"
        )

    except Exception as e:
        logger.error(f"Failed to create new game: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create new game: {str(e)}"
        )


@router.get("/{session_id}/state", response_model=GameStateResponse)
async def get_game_state(session_id: str, db: Session = Depends(get_db)):
    """
    Get the current game state for a session.

    Args:
        session_id (str): Game session ID
        db (Session): Database session

    Returns:
        GameStateResponse: Current game state
    """
    try:
        logger.info(f"Retrieving game state for session: {session_id}")

        # Get game session from database
        db_game_session = get_game_session(db, session_id)
        if not db_game_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Game session {session_id} not found"
            )

        # Get conversation history from database
        conversation_history = get_conversation_history(db, session_id)

        # Create response
        response = GameStateResponse(
            session_id=db_game_session.id,
            player_character=db_game_session.character_data,
            party_members=db_game_session.party_data,
            recruitable_characters=db_game_session.recruitable_characters_data,
            active_quests=db_game_session.quests_data,
            world_context=db_game_session.world_data,
            inventory=db_game_session.inventory_data,
            combat_state=db_game_session.combat_state_data,
            narrative="",  # No new narrative for state requests
            new_options=[],  # No new options for state requests
            game_flags=db_game_session.game_flags_data,
            conversation_history=conversation_history
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve game state: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve game state: {str(e)}"
        )


@router.post("/{session_id}/action", response_model=GameStateResponse)
async def process_game_action(session_id: str, request: ActionRequest, db: Session = Depends(get_db)):
    """
    Process a player action in the game.

    Args:
        session_id (str): Game session ID
        request (ActionRequest): Player's action
        db (Session): Database session

    Returns:
        GameStateResponse: Updated game state with narrative response
    """
    try:
        logger.info(f"Processing action for session {session_id}: {request.action_type} - {request.value}")

        # Get game session from database
        db_game_session = get_game_session(db, session_id)
        if not db_game_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Game session {session_id} not found"
            )

        # Create game state from database data
        try:
            created_at_str = db_game_session.created_at.isoformat() if db_game_session.created_at else datetime.now().isoformat()
            last_updated_str = db_game_session.last_updated.isoformat() if db_game_session.last_updated else datetime.now().isoformat()
        except Exception as e:
            logger.error(f"Error accessing datetime fields: {str(e)}")
            created_at_str = datetime.now().isoformat()
            last_updated_str = datetime.now().isoformat()

        game_state_dict = {
            "session_id": db_game_session.id,
            "player_character": db_game_session.character_data,
            "party_members": db_game_session.party_data,
            "recruitable_characters": db_game_session.recruitable_characters_data,
            "active_quests": db_game_session.quests_data,
            "world_context": db_game_session.world_data,
            "inventory": db_game_session.inventory_data,
            "combat_state": db_game_session.combat_state_data,
            "game_flags": db_game_session.game_flags_data,
            "conversation_history": [],
            "created_at": created_at_str,
            "last_updated": last_updated_str
        }
        game_state = GameState.from_dict(game_state_dict)

        # Get conversation history from database
        conversation_history = get_conversation_history(db, session_id)
        game_state.conversation_history = conversation_history

        # Add player action to conversation history
        player_conversation = {
            "timestamp": datetime.now().isoformat(),
            "type": "player",
            "content": request.value
        }
        game_state.conversation_history.append(player_conversation)

        # Save player action
        save_conversation_entry(db, session_id, "player", request.value)
        save_game_action(db, session_id, request.action_type, request.value)

        # Process action with AI Game Master
        ai_gm = AIGameMaster()
        action_result = ai_gm.process_player_action(
            game_state.to_dict(),
            request.value
        )

        # Add AI response to conversation history
        ai_conversation = {
            "timestamp": datetime.now().isoformat(),
            "type": "narrative",
            "content": action_result["narrative"]
        }
        game_state.conversation_history.append(ai_conversation)

        # Save AI response
        save_conversation_entry(db, session_id, "narrative", action_result["narrative"])
        save_game_action(db, session_id, "ai_response", request.value, action_result["narrative"])

        # Update game state in database
        updated_game_state_dict = game_state.to_dict()
        update_game_session(db, session_id, updated_game_state_dict)

        # Create response
        response = GameStateResponse(
            session_id=game_state.session_id,
            player_character=game_state.player_character,
            party_members=game_state.party_members,
            recruitable_characters=game_state.recruitable_characters,
            active_quests=game_state.active_quests,
            world_context=game_state.world_context,
            inventory=game_state.inventory,
            combat_state=game_state.combat_state,
            narrative=action_result["narrative"],
            new_options=action_result["new_options"],
            game_flags=game_state.game_flags,
            conversation_history=game_state.conversation_history
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"Failed to process game action: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error args: {e.args}")
        raise


@router.get("/{session_id}/save", response_model=dict)
async def save_game_state(session_id: str, db: Session = Depends(get_db)):
    """
    Manually save the current game state.

    Args:
        session_id (str): Game session ID
        db (Session): Database session

    Returns:
        dict: Save confirmation
    """
    try:
        # Get game session from database
        db_game_session = get_game_session(db, session_id)
        if not db_game_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Game session {session_id} not found"
            )

        logger.info(f"Game state saved for session {session_id}")

        return {"message": "Game saved successfully", "session_id": session_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save game state: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save game state: {str(e)}"
        )


@router.post("/load", response_model=GameStateResponse)
async def load_game_state(request: dict, db: Session = Depends(get_db)):
    """
    Load a saved game state.

    Args:
        request (dict): Request containing session_id
        db (Session): Database session

    Returns:
        GameStateResponse: Loaded game state
    """
    try:
        session_id = request.get("session_id")
        if not session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="session_id is required"
            )

        logger.info(f"Loading game state for session: {session_id}")

        # Get game session from database
        db_game_session = get_game_session(db, session_id)
        if not db_game_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Game session {session_id} not found"
            )

        # Get conversation history from database
        conversation_history = get_conversation_history(db, session_id)

        # Create response
        response = GameStateResponse(
            session_id=db_game_session.id,
            player_character=db_game_session.character_data,
            party_members=db_game_session.party_data,
            recruitable_characters=db_game_session.recruitable_characters_data,
            active_quests=db_game_session.quests_data,
            world_context=db_game_session.world_data,
            inventory=db_game_session.inventory_data,
            combat_state=db_game_session.combat_state_data,
            narrative="Game loaded successfully. Continue your adventure!",
            new_options=["Look around", "Check inventory", "Rest"],
            game_flags=db_game_session.game_flags_data,
            conversation_history=conversation_history
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load game state: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load game state: {str(e)}"
        )
