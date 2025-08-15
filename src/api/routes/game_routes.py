from fastapi import APIRouter, HTTPException, status
from typing import Dict
from src.api.api_models import (
    NewGameRequest,
    ActionRequest,
    GameStateResponse,
    GameCreationResponse
)
from src.core.game_state import GameState, save_game, load_game
from src.core.engine.character_creation import create_new_character
from src.ai.ai_gm import AIGameMaster
import logging
import uuid
import os

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# In-memory storage for active game sessions (in production, use a database)
active_sessions: Dict[str, GameState] = {}

@router.post("/new", response_model=GameCreationResponse)
async def create_new_game(request: NewGameRequest):
    """
    Create a new game session.

    Args:
        request (NewGameRequest): Player's initial choices

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

        # Add initial narrative from AI
        initial_prompt = f"Welcome {request.player_name}, a {request.player_race.value} {request.player_class.value}. {character_details['backstory'][:100]}... You find yourself in {world_data.get('region_name', 'the starting region')}."
        action_result = ai_gm.process_player_action(
            game_state.to_dict(),
            f"Look around {world_data.get('region_name', 'the area')}"
        )

        # Create response
        game_state_response = GameStateResponse(
            session_id=session_id,
            player_character=player_character,
            party_members=game_state.party_members,
            active_quests=game_state.active_quests,
            world_context=game_state.world_context,
            inventory=game_state.inventory,
            combat_state=game_state.combat_state,
            narrative=action_result["narrative"],
            new_options=action_result["new_options"],
            game_flags=game_state.game_flags
        )

        # Store session
        active_sessions[session_id] = game_state

        # Save game state
        save_game(game_state)

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
async def get_game_state(session_id: str):
    """
    Get the current game state for a session.

    Args:
        session_id (str): Game session ID

    Returns:
        GameStateResponse: Current game state
    """
    try:
        logger.info(f"Retrieving game state for session: {session_id}")

        # Check active sessions first
        if session_id in active_sessions:
            game_state = active_sessions[session_id]
        else:
            # Try to load from file
            save_file = f"saves/{session_id}.json"
            if os.path.exists(save_file):
                game_state = load_game(save_file)
                active_sessions[session_id] = game_state
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Game session {session_id} not found"
                )

        # Create response
        response = GameStateResponse(
            session_id=game_state.session_id,
            player_character=game_state.player_character,
            party_members=game_state.party_members,
            active_quests=game_state.active_quests,
            world_context=game_state.world_context,
            inventory=game_state.inventory,
            combat_state=game_state.combat_state,
            narrative="",  # No new narrative for state requests
            new_options=[],  # No new options for state requests
            game_flags=game_state.game_flags
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
async def process_game_action(session_id: str, request: ActionRequest):
    """
    Process a player action in the game.

    Args:
        session_id (str): Game session ID
        request (ActionRequest): Player's action

    Returns:
        GameStateResponse: Updated game state with narrative response
    """
    try:
        logger.info(f"Processing action for session {session_id}: {request.action_type} - {request.value}")

        # Get game state
        if session_id not in active_sessions:
            # Try to load from file
            save_file = f"saves/{session_id}.json"
            if os.path.exists(save_file):
                game_state = load_game(save_file)
                active_sessions[session_id] = game_state
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Game session {session_id} not found"
                )
        else:
            game_state = active_sessions[session_id]

        # Process action with AI Game Master
        ai_gm = AIGameMaster()
        action_result = ai_gm.process_player_action(
            game_state.to_dict(),
            request.value
        )

        # Update game state
        game_state.last_updated = __import__('datetime').datetime.now()

        # Create response
        response = GameStateResponse(
            session_id=game_state.session_id,
            player_character=game_state.player_character,
            party_members=game_state.party_members,
            active_quests=game_state.active_quests,
            world_context=game_state.world_context,
            inventory=game_state.inventory,
            combat_state=game_state.combat_state,
            narrative=action_result["narrative"],
            new_options=action_result["new_options"],
            game_flags=game_state.game_flags
        )

        # Save updated game state
        save_game(game_state)

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process game action: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process game action: {str(e)}"
        )


@router.get("/{session_id}/save", response_model=dict)
async def save_game_state(session_id: str):
    """
    Manually save the current game state.

    Args:
        session_id (str): Game session ID

    Returns:
        dict: Save confirmation
    """
    try:
        if session_id not in active_sessions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Game session {session_id} not found"
            )

        game_state = active_sessions[session_id]
        save_path = save_game(game_state)

        logger.info(f"Game state saved for session {session_id} to {save_path}")

        return {"message": "Game saved successfully", "save_path": save_path}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save game state: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save game state: {str(e)}"
        )
