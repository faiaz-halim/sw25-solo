class ApiService {
    constructor() {
        // Use relative path for Docker deployment, fallback to localhost for direct development
        this.baseUrl = 'http://localhost:8000/api/game';
    }

    async newGame(playerName, playerRace, playerClass) {
        try {
            const response = await fetch(`${this.baseUrl}/new`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    player_name: playerName,
                    player_race: playerRace,
                    player_class: playerClass
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error creating new game:', error);
            throw error;
        }
    }

    async postAction(sessionId, action) {
        try {
            const response = await fetch(`${this.baseUrl}/${sessionId}/action`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    action_type: 'text',
                    value: action
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error posting action:', error);
            throw error;
        }
    }

    async getState(sessionId) {
        try {
            const response = await fetch(`${this.baseUrl}/${sessionId}/state`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error getting game state:', error);
            throw error;
        }
    }
}

class UIManager {
    constructor() {
        this.narrativeContent = document.getElementById('narrative-content');
        this.characterInfo = document.getElementById('character-info');
        this.partyMembers = document.getElementById('party-members');
        this.sessionIdSpan = document.getElementById('session-id');
    }

    showScreen(screenId) {
        // Hide all screens
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.add('hidden');
        });

        // Show the requested screen
        document.getElementById(screenId).classList.remove('hidden');
    }

    updateNarrative(text) {
        if (text) {
            const paragraph = document.createElement('p');
            paragraph.textContent = text;
            this.narrativeContent.appendChild(paragraph);

            // Scroll to bottom
            this.narrativeContent.scrollTop = this.narrativeContent.scrollHeight;
        }
    }

    updateCharacterSheet(characterData) {
        if (!characterData) return;

        let html = `
            <div class="character-info-item">
                <div class="character-info-label">Name</div>
                <div class="character-info-value">${characterData.name}</div>
            </div>
            <div class="character-info-item">
                <div class="character-info-label">Race/Class</div>
                <div class="character-info-value">${characterData.race} ${characterData.character_class}</div>
            </div>
            <div class="character-info-item">
                <div class="character-info-label">Level</div>
                <div class="character-info-value">${characterData.level}</div>
            </div>
        `;

        // Stats grid
        html += `
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-label">HP</div>
                    <div class="stat-value">${characterData.hit_points}/${characterData.max_hit_points}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">MP</div>
                    <div class="stat-value">${characterData.magic_points}/${characterData.max_magic_points}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">STR</div>
                    <div class="stat-value">${characterData.strength}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">DEX</div>
                    <div class="stat-value">${characterData.dexterity}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">VIT</div>
                    <div class="stat-value">${characterData.vitality}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">INT</div>
                    <div class="stat-value">${characterData.intelligence}</div>
                </div>
            </div>
        `;

        this.characterInfo.innerHTML = html;
    }

    updateParty(partyData) {
        if (!partyData || partyData.length === 0) {
            this.partyMembers.innerHTML = '<p class="text-muted">No party members yet</p>';
            return;
        }

        let html = '';
        partyData.forEach(member => {
            html += `
                <div class="party-member">
                    <div class="party-member-name">${member.name}</div>
                    <div class="party-member-class">${member.race} ${member.character_class} (Level ${member.level})</div>
                </div>
            `;
        });

        this.partyMembers.innerHTML = html;
    }

    showSessionId(sessionId) {
        this.sessionIdSpan.textContent = sessionId;
        document.getElementById('session-info').classList.remove('hidden');
    }

    clearNarrative() {
        this.narrativeContent.innerHTML = '';
    }
}

class GameApp {
    constructor() {
        this.apiService = new ApiService();
        this.uiManager = new UIManager();
        this.sessionId = null;
        this.gameState = null;

        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // New game form submission
        const newGameForm = document.getElementById('new-game-form');
        if (newGameForm) {
            newGameForm.addEventListener('submit', (e) => this.handleNewGame(e));
        }

        // Action input form submission
        const inputForm = document.getElementById('input-form');
        if (inputForm) {
            inputForm.addEventListener('submit', (e) => this.handleActionInput(e));
        }
    }

    async handleNewGame(event) {
        event.preventDefault();

        const playerName = document.getElementById('player-name').value;
        const playerRace = document.getElementById('player-race').value;
        const playerClass = document.getElementById('player-class').value;

        if (!playerName || !playerRace || !playerClass) {
            alert('Please fill in all fields');
            return;
        }

        try {
            // Show loading screen
            this.uiManager.showScreen('loading-screen');

            // Create new game
            const response = await this.apiService.newGame(playerName, playerRace, playerClass);

            this.sessionId = response.session_id;
            this.gameState = response.initial_state;

            // Update UI
            this.uiManager.showSessionId(this.sessionId);
            this.uiManager.updateCharacterSheet(this.gameState.player_character);
            this.uiManager.updateParty(this.gameState.party_members);
            this.uiManager.clearNarrative();
            this.uiManager.updateNarrative(this.gameState.narrative);

            // Show game screen
            this.uiManager.showScreen('game-screen');

        } catch (error) {
            console.error('Failed to create new game:', error);
            alert('Failed to create new game. Please try again.');
            this.uiManager.showScreen('new-game-screen');
        }
    }

    async handleActionInput(event) {
        event.preventDefault();

        const playerInput = document.getElementById('player-input');
        const action = playerInput.value.trim();

        if (!action) return;

        if (!this.sessionId) {
            alert('No active game session');
            return;
        }

        try {
            // Clear input
            playerInput.value = '';

            // Add player action to narrative
            this.uiManager.updateNarrative(`> ${action}`);

            // Send action to server
            const response = await this.apiService.postAction(this.sessionId, action);

            // Update game state
            this.gameState = response;

            // Update UI
            this.uiManager.updateCharacterSheet(this.gameState.player_character);
            this.uiManager.updateParty(this.gameState.party_members);
            this.uiManager.updateNarrative(this.gameState.narrative);

        } catch (error) {
            console.error('Failed to process action:', error);
            this.uiManager.updateNarrative('Sorry, I encountered an error processing your action. Please try again.');
        }
    }
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.gameApp = new GameApp();
    console.log('Sword World 2.5 AI GM initialized');
});
