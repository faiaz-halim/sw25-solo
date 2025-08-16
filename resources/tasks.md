# Sword World 2.5 AI GM - Detailed Task Breakdown

This document provides a comprehensive list of tasks and subtasks for the development of the Sword World 2.5 AI GM project, designed for clarity and use with code generation tools.

---

## **Phase 0: Project Setup & Pre-production**

### **1. Core Infrastructure**
- **1.1. Version Control Setup**
    - 1.1.1. Initialize a Git repository.
    - 1.1.2. Create main branches (`main`, `develop`).
    - 1.1.3. Establish a branching strategy (e.g., GitFlow).
    - 1.1.4. Configure `.gitignore` for Python, Godot, and IDE files.
- **1.2. Backend Environment Setup**
    - 1.2.1. Set up a Python virtual environment (e.g., `venv` or `conda`).
    - 1.2.2. Create `requirements.txt` file.
    - 1.2.3. Install core dependencies: `fastapi`, `uvicorn`, `requests`, `pydantic`.
- **1.3. API & Credentials Management**
    - 1.3.1. Obtain an API key for OpenRouter.
    - 1.3.2. Implement a secure way to manage secrets (e.g., environment variables, `.env` file).

---

## **Phase 1: Backend & Web-Based Chat Interface**

### **Module 1: Core Game Logic & Rules Engine (Backend - Python)**
- **1.1. Data Model Implementation (`/core/models/`)**
    - 1.1.1. Create `dice.py`: Implement a `roll_dice(notation: str) -> int` utility.
    - 1.1.2. Create `attributes.py`: Define Pydantic models for `enums` like `SkillType`, `Race`, `Class`, `ItemType`.
    - 1.1.3. Create `item.py`: Implement `Item`, `Weapon`, `Armor`, and `Accessory` data classes with stats from the rulebook.
    - 1.1.4. Create `spell.py`: Implement `Spell` data class with attributes like MP cost, range, effect.
    - 1.1.5. Create `character.py`:
        - 1.1.5.1. Implement `CharacterSheet` class using Pydantic.
        - 1.1.5.2. Include fields for all stats: HP, MP, Dexterity, Strength, Vitality, Intelligence, Spirit, etc.
        - 1.1.5.3. Include lists for `skills`, `spells`, `inventory`, `equipment`.
        - 1.1.5.4. Implement methods: `calculate_derived_stats()` (e.g., HP, MP, defense), `equip_item(item)`, `unequip_item(item)`, `take_damage(amount)`, `is_alive()`.
    - 1.1.6. Create `monster.py`: Implement `Monster` data class with stats, abilities, and loot tables based on the rulebook [p. 388].
    - 1.1.7. Create `quest.py`: Implement `Quest` data class with fields for `title`, `description`, `objectives` (list of strings), and `status` (enum: NotStarted, InProgress, Completed).
- **1.2. Ruleset & Game Mechanics Implementation (`/core/engine/`)**
    - 1.2.1. Create `skill_checks.py`: Implement `perform_skill_check(character: Character, skill: SkillType, difficulty: int) -> bool`.
    - 1.2.2. Create `character_creation.py`:
        - 1.2.2.1. Implement `roll_on_history_table()` -> str.
        - 1.2.2.2. Implement `roll_on_adventure_reason_table()` -> str.
        - 1.2.2.3. Implement `create_new_character(race: Race, class: Class, backstory_elements: dict) -> CharacterSheet`.
    - 1.2.3. Create `combat_manager.py`:
        - 1.2.3.1. Implement `CombatManager` class to manage a combat encounter.
        - 1.2.3.2. Method: `start_combat(party: list[Character], enemies: list[Monster])`.
        - 1.2.3.3. Method: `calculate_initiative()` to determine turn order.
        - 1.2.3.4. Method: `process_turn(character, action, target)`.
        - 1.2.3.5. Method: `handle_attack(attacker, defender)` -> dict (damage, hit/miss).
        - 1.2.3.6. Method: `handle_spell(caster, spell, target)`.
        - 1.2.3.7. Method: `check_end_condition()` -> bool.
- **1.3. Game State Management (`/core/`)**
    - 1.3.1. Create `game_state.py`:
        - 1.3.1.1. Implement `GameState` class to hold all session data: `session_id`, `player_character`, `party_members`, `active_quests`, `world_context`, `current_location`, `combat_state`.
        - 1.3.1.2. Implement `save_game(state)` and `load_game(session_id)` methods (initially to a local JSON file or in-memory dictionary).

### **Module 2: AI Game Master & Content Generation (Backend - Python)**
- **2.1. AI Service Interface (`/ai/`)**
    - 2.1.1. Create `openrouter_client.py`:
        - 2.1.1.1. Implement `call_llm(prompt: str, system_prompt: str) -> dict`.
        - 2.1.1.2. Handle API key loading from environment variables.
        - 2.1.1.3. Implement robust error handling, JSON parsing, and retry logic.
- **2.2. Prompt Engineering (`/ai/prompts/`)**
    - 2.2.1. Create `system_prompts.py`: Define the master system prompt for the AI GM, enforcing the role and rules.
    - 2.2.2. Create `world_generation.py`: Function `generate_world_prompt()` to create the starting region.
    - 2.2.3. Create `character_generation.py`: Function `generate_backstory_prompt(race, class, history_rolls)` to generate a character's origin story.
    - 2.2.4. Create `quest_generation.py`: Function `generate_quest_prompt(game_state)` to create a new quest based on context.
    - 2.2.5. Create `action_processing.py`: Function `generate_action_prompt(game_state, player_input)` to process a player's action and generate a narrative response.
    - 2.2.6. Create `npc_interaction.py`: Function `generate_npc_dialogue_prompt(npc_personality, player_dialogue)` for dynamic conversations.
- **2.3. AI-Driven Game Logic (`/ai/`)**
    - 2.3.1. Create `ai_gm.py`:
        - 2.3.1.1. Function `generate_initial_world()` -> dict (description, locations).
        - 2.3.1.2. Function `generate_player_character_details(race, class)` -> dict (backstory, attributes).
        - 2.3.1.3. Function `generate_recruitable_npcs(count)` -> list[CharacterSheet].
        - 2.3.1.4. Function `process_player_action(game_state, player_input)` -> dict (narration, state_changes). This function will orchestrate calling the `RulesEngine` for checks and the LLM for narration.

### **Module 3: API Server (Backend - FastAPI)**
- **3.1. API Structure (`/api/`)**
    - 3.1.1. Create `main.py` to initialize the FastAPI application.
    - 3.1.2. Create `api_models.py` for Pydantic request/response models (e.g., `NewGameRequest`, `ActionRequest`, `GameStateResponse`).
    - 3.1.3. Implement CORS middleware to allow requests from the web frontend.
- **3.2. RESTful Endpoints (`/api/routes/`)**
    - 3.2.1. Create `game_routes.py`:
        - 3.2.1.1. `POST /api/game/new`:
            - Takes `NewGameRequest` (player race/class choice).
            - Calls `ai_gm.generate_initial_world()` and `character_creation` modules.
            - Creates a new `GameState` instance.
            - Saves and returns the initial `GameStateResponse`.
        - 3.2.1.2. `GET /api/game/{session_id}/state`:
            - Loads the game state for the given `session_id`.
            - Returns the current `GameStateResponse`.
        - 3.2.1.3. `POST /api/game/{session_id}/action`:
            - Takes `ActionRequest` (e.g., text command).
            - Loads the current game state.
            - Passes the action to `ai_gm.process_player_action()`.
            - Updates and saves the game state.
            - Returns the `GameStateResponse` with the new narration and state.

### **Module 4: Web-Based Chat Interface (Phase 1 Frontend)**
- **4.1. Project Structure**
    - 4.1.1. Create `index.html` for the main page structure.
    - 4.1.2. Create `style.css` for UI styling.
    - 4.1.3. Create `app.js` for all client-side logic.
- **4.2. UI Components (`index.html` & `style.css`)**
    - 4.2.1. Create a container for the game interface.
    - 4.2.2. Design and implement the narrative window (`div#narrative-window`).
    - 4.2.3. Design and implement the player input form (`form#input-form` with a text input).
    - 4.2.4. Design and implement the character sheet panel (`div#character-sheet`).
    - 4.2.5. Design and implement the party member panel (`div#party-panel`).
- **4.3. Client-Side Logic (`app.js`)**
    - 4.3.1. Implement a `ApiService` class/module to handle `fetch` calls to the backend.
        - 4.3.1.1. `newGame(race, class)` function.
        - 4.3.1.2. `postAction(sessionId, action)` function.
        - 4.3.1.3. `getState(sessionId)` function.
    - 4.3.2. Implement a `UIManager` class/module.
        - 4.3.2.1. `updateNarrative(text)` function to append text to the narrative window and scroll down.
        - 4.3.2.2. `updateCharacterSheet(characterData)` function to populate the sidebar.
        - 4.3.2.3. `updateParty(partyData)` function.
    - 4.3.3. Add event listener to the input form to capture player commands.
    - 4.3.4. Implement the main game loop logic:
        - 4.3.4.1. On page load, show the new game creation screen.
        - 4.3.4.2. On new game start, call `ApiService.newGame()`, store the `sessionId`, and render the initial state.
        - 4.3.4.3. On form submission, call `ApiService.postAction()` and update the UI with the response.

---

## **Phase 2: Godot Isometric Client**

### **Module 5: Godot Project Setup & Core Systems**
- **5.1. Project Initialization**
    - 5.1.1. Create a new Godot 4 project.
    - 5.1.2. Set up the project directory structure (`scenes`, `scripts`, `assets`, `ui`).
    - 5.1.3. Configure display settings for an isometric game.
- **5.2. Backend Communication System**
    - 5.2.1. Create a global autoload script (singleton) named `APIClient.gd`.
    - 5.2.2. In `APIClient.gd`, implement functions to wrap `HTTPRequest` node calls for each backend endpoint (`new_game`, `post_action`, `get_state`).
    - 5.2.3. Implement signal handling for request completion (`request_completed` signal).
- **5.3. Game State Management (Client-Side)**
    - 5.3.1. Create a global autoload script `GameStateClient.gd`.
    - 5.3.2. This script will hold the local copy of the game state received from the backend.
    - 5.3.3. Implement functions to update the local state from an API response and emit signals when data changes (e.g., `signal player_stats_changed`).

### **Module 6: World & Character Rendering**
- **6.1. Art Assets**
    - 6.1.1. Acquire or create isometric tile sets for environments.
    - 6.1.2. Acquire or create animated sprites for characters and monsters.
- **6.2. Scene Creation (`/scenes/`)**
    - 6.2.1. Create `Player.tscn` (`CharacterBody2D`) with `Sprite2D` and `AnimationPlayer`.
    - 6.2.2. Create `NPC.tscn` and `Monster.tscn`, similar to the player scene.
    - 6.2.3. Create `GameWorld.tscn` as the main gameplay scene.
        - 6.2.3.1. Add a `TileMap` node for rendering the environment.
        - 6.2.3.2. Add a `Camera2D` configured for the player.
- **6.3. Rendering Logic (`/scripts/`)**
    - 6.3.1. Create `game_world.gd` script for `GameWorld.tscn`.
    - 6.3.2. Implement a function `render_state(state_data)` that:
        - 6.3.2.1. Clears existing NPCs/monsters.
        - 6.3.2.2. Parses the `world_context` from the backend to draw the `TileMap`.
        - 6.3.2.3. Instantiates and positions `Player.tscn`, `NPC.tscn`, and `Monster.tscn` based on data from the backend.
        - 6.3.2.4. Connects to `GameStateClient` signals to receive updates.

### **Module 7: UI/UX & Player Input**
- **7.1. UI Scene Creation (`/ui/`)**
    - 7.1.1. Create `MainMenu.tscn` with "New Game" and "Load Game" buttons.
    - 7.1.2. Create `CharacterCreation.tscn` with widgets for race/class selection.
    - 7.1.3. Create `GameHUD.tscn` as a canvas layer to be overlaid on `GameWorld.tscn`.
        - 7.1.3.1. Re-implement the narrative/log window using `RichTextLabel`.
        - 7.1.3.2. Re-implement the text input using `LineEdit`.
        - 7.1.3.3. Re-implement the character sheet display using Godot's `Control` nodes.
- **7.2. Input Handling (`/scripts/`)**
    - 7.2.1. In `game_world.gd`, implement `_unhandled_input(event)` function.
    - 7.2.2. Implement point-and-click movement: on mouse click, get tile coordinates and send a "move_to" action to the backend via `APIClient`.
    - 7.2.3. Implement interaction: on clicking an NPC, send an "interact" action.
    - 7.2.4. Connect the `LineEdit` node's `text_submitted` signal to a function that sends a "text" action to the backend.
