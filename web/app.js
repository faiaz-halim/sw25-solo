class ApiService {
    constructor() {
        // Use relative path for Docker deployment, fallback to localhost for direct development
        this.baseUrl = 'http://localhost:8000/api/game';
    }

    async newGame(playerName, playerRace, playerClass, historyChoice = null, adventureReasonChoice = null) {
        try {
            const requestBody = {
                player_name: playerName,
                player_race: playerRace,
                player_class: playerClass
            };

            // Add backstory choices if provided
            if (historyChoice) {
                requestBody.history_choice = parseInt(historyChoice);
            }
            if (adventureReasonChoice) {
                requestBody.adventure_reason_choice = parseInt(adventureReasonChoice);
            }

            const response = await fetch(`${this.baseUrl}/new`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
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
        this.historyTabContent = document.getElementById('history-tab-content');
        this.historyModalContent = document.getElementById('history-content');
        this.initializeTabs();
    }

    initializeTabs() {
        // Add event listeners for tab buttons
        const tabButtons = document.querySelectorAll('.tab-btn');
        tabButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const tabName = e.target.getAttribute('data-tab');
                this.switchTab(tabName);
            });
        });
    }

    switchTab(tabName) {
        // Hide all tab contents
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });

        // Remove active class from all tab buttons
        document.querySelectorAll('.tab-btn').forEach(button => {
            button.classList.remove('active');
        });

        // Show selected tab content
        document.getElementById(`${tabName}-tab`).classList.add('active');

        // Add active class to clicked button
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    }

    showScreen(screenId) {
        // Hide all screens
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.add('hidden');
        });

        // Show the requested screen
        document.getElementById(screenId).classList.remove('hidden');
    }

    updateNarrative(gameState) {
        if (!gameState) return;

        // Clear existing content
        this.narrativeContent.innerHTML = '';

        // Display world description first
        if (gameState.world_context && gameState.world_context.world_description) {
            const worldDescElement = document.createElement('div');
            worldDescElement.className = 'world-description-section';
            worldDescElement.innerHTML = `<h3>Location: ${gameState.world_context.current_location || 'Unknown'}</h3>
                                          <p>${this.formatText(gameState.world_context.world_description)}</p>`;
            this.narrativeContent.appendChild(worldDescElement);
        }

        // Display narrative content
        if (gameState.narrative) {
            const narrativeElement = document.createElement('div');
            narrativeElement.className = 'narrative-section';

            // Split narrative by double newlines and create separate paragraphs
            const paragraphs = gameState.narrative.split('\n\n');
            paragraphs.forEach(paragraphText => {
                if (paragraphText.trim()) {
                    const paragraph = document.createElement('p');
                    paragraph.innerHTML = this.formatText(paragraphText);
                    narrativeElement.appendChild(paragraph);
                }
            });

            this.narrativeContent.appendChild(narrativeElement);
        }

        // Display new options
        if (gameState.new_options && gameState.new_options.length > 0) {
            const optionsElement = document.createElement('div');
            optionsElement.className = 'options-section';
            optionsElement.innerHTML = '<h4>What would you like to do?</h4>';

            // Create a container for the dynamic action buttons
            const actionsContainer = document.createElement('div');
            actionsContainer.className = 'dynamic-actions-grid';
            actionsContainer.style.display = 'grid';
            actionsContainer.style.gridTemplateColumns = 'repeat(2, 1fr)';
            actionsContainer.style.gap = '10px';
            actionsContainer.style.marginTop = '10px';

            gameState.new_options.forEach(option => {
                const actionButton = document.createElement('button');
                actionButton.textContent = option;
                actionButton.className = 'dynamic-action-btn';

                // Add click handler
                actionButton.addEventListener('click', () => {
                    if (window.gameApp) {
                        window.gameApp.handleActionInputFromOption(option);
                    }
                });

                actionsContainer.appendChild(actionButton);
            });
            optionsElement.appendChild(actionsContainer);

            this.narrativeContent.appendChild(optionsElement);
        }

        // Scroll to bottom
        this.narrativeContent.scrollTop = this.narrativeContent.scrollHeight;
    }

    updateConversationHistory(conversationHistory) {
        this.conversationHistory = conversationHistory || [];

        // Update both tab content and modal content
        this.updateHistoryTabContent();
        this.updateHistoryModalContent();
    }

    updateHistoryTabContent() {
        if (!this.historyTabContent) return;

        // Clear existing content
        this.historyTabContent.innerHTML = '';

        // Display conversation history
        if (this.conversationHistory && this.conversationHistory.length > 0) {
            this.conversationHistory.forEach(entry => {
                const entryElement = document.createElement('div');
                entryElement.className = `history-entry history-${entry.type}`;

                const timestamp = new Date(entry.timestamp).toLocaleString();
                entryElement.innerHTML = `
                    <div class="history-timestamp">${timestamp}</div>
                    <div class="history-content-text">${this.formatText(entry.content)}</div>
                `;

                this.historyTabContent.appendChild(entryElement);
            });
        } else {
            this.historyTabContent.innerHTML = '<p class="text-muted">No conversation history yet.</p>';
        }

        // Scroll to bottom
        this.historyTabContent.scrollTop = this.historyTabContent.scrollHeight;
    }

    updateHistoryModalContent() {
        if (!this.historyModalContent) return;

        // Clear existing content
        this.historyModalContent.innerHTML = '';

        // Display conversation history
        if (this.conversationHistory && this.conversationHistory.length > 0) {
            this.conversationHistory.forEach(entry => {
                const entryElement = document.createElement('div');
                entryElement.className = `history-entry history-${entry.type}`;

                const timestamp = new Date(entry.timestamp).toLocaleString();
                entryElement.innerHTML = `
                    <div class="history-timestamp">${timestamp}</div>
                    <div class="history-content-text">${this.formatText(entry.content)}</div>
                `;

                this.historyModalContent.appendChild(entryElement);
            });
        } else {
            this.historyModalContent.innerHTML = '<p class="text-muted">No conversation history yet.</p>';
        }

        // Scroll to bottom
        this.historyModalContent.scrollTop = this.historyModalContent.scrollHeight;
    }

    showConversationHistory() {
        const modal = document.getElementById('history-modal');

        if (!this.historyModalContent) return;

        // Update modal content
        this.updateHistoryModalContent();

        // Show modal
        modal.classList.remove('hidden');

        // Scroll to bottom
        this.historyModalContent.scrollTop = this.historyModalContent.scrollHeight;
    }

    hideConversationHistory() {
        const modal = document.getElementById('history-modal');
        modal.classList.add('hidden');
    }

    formatText(text) {
        if (!text) return '';

        // Handle single newlines within paragraphs and basic markdown
        let formattedText = text.replace(/\n/g, '<br>');

        // Handle bold text (**text** or __text__)
        formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        formattedText = formattedText.replace(/__(.*?)__/g, '<strong>$1</strong>');

        // Handle italic text (*text* or _text_)
        formattedText = formattedText.replace(/\*(.*?)\*/g, '<em>$1</em>');
        formattedText = formattedText.replace(/_(.*?)_/g, '<em>$1</em>');

        // Handle headers (# Header, ## Header, etc.)
        formattedText = formattedText.replace(/^### (.*?)(<br>|$)/g, '<h3>$1</h3>');
        formattedText = formattedText.replace(/^## (.*?)(<br>|$)/g, '<h2>$1</h2>');
        formattedText = formattedText.replace(/^# (.*?)(<br>|$)/g, '<h1>$1</h1>');

        return formattedText;
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

    updateCharacterBackground(characterData) {
        if (!characterData) return;

        const backstoryElement = document.getElementById('character-backstory');
        if (backstoryElement && characterData.backstory) {
            // Show full background text without clipping
            backstoryElement.innerHTML = `<div>${characterData.backstory}</div>`;
        }
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

    updateCommonActions() {
        const commonActionsElement = document.getElementById('common-actions');
        if (!commonActionsElement) return;

        // Common actions consistent with Sword World 2.5 rules
        const commonActions = [
            { label: "Look Around", action: "Look around" },
            { label: "Search Area", action: "Search the area carefully" },
            { label: "Talk to Party", action: "Talk to my party members" },
            { label: "Check Inventory", action: "Check my inventory" },
            { label: "Rest", action: "Rest and recover" },
            { label: "Move Forward", action: "Move forward" }
        ];

        let html = '';
        commonActions.forEach(action => {
            html += `
                <button class="common-action-btn" data-action="${action.action}">
                    ${action.label}
                </button>
            `;
        });

        commonActionsElement.innerHTML = html;

        // Add event listeners to the action buttons
        document.querySelectorAll('.common-action-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                const action = e.target.getAttribute('data-action');
                if (action && window.gameApp) {
                    window.gameApp.handleCommonAction(action);
                }
            });
        });
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

        // Save game button
        const saveGameBtn = document.getElementById('save-game-btn');
        if (saveGameBtn) {
            saveGameBtn.addEventListener('click', () => this.handleSaveGame());
        }

        // Show history button
        const showHistoryBtn = document.getElementById('show-history-btn');
        if (showHistoryBtn) {
            showHistoryBtn.addEventListener('click', () => this.handleShowHistory());
        }

        // Close modal buttons
        const closeButtons = document.querySelectorAll('.close');
        closeButtons.forEach(button => {
            button.addEventListener('click', () => this.handleCloseModals());
        });

        // Close modals when clicking outside
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.handleCloseModals();
                }
            });
        });

        // Load game form submission
        const loadGameForm = document.getElementById('load-game-form');
        if (loadGameForm) {
            loadGameForm.addEventListener('submit', (e) => this.handleLoadGame(e));
        }
    }

    async handleNewGame(event) {
        event.preventDefault();

        const playerName = document.getElementById('player-name').value;
        const playerRace = document.getElementById('player-race').value;
        const playerClass = document.getElementById('player-class').value;
        const historyChoice = document.getElementById('history-choice').value;
        const adventureReasonChoice = document.getElementById('adventure-reason-choice').value;

        if (!playerName || !playerRace || !playerClass) {
            alert('Please fill in all required fields');
            return;
        }

        try {
            // Show loading screen
            this.uiManager.showScreen('loading-screen');

            // Create new game with backstory choices
            const response = await this.apiService.newGame(
                playerName,
                playerRace,
                playerClass,
                historyChoice || null,
                adventureReasonChoice || null
            );

            this.sessionId = response.session_id;
            this.gameState = response.initial_state;

            // Update UI
            this.uiManager.showSessionId(this.sessionId);
            this.uiManager.updateCharacterSheet(this.gameState.player_character);
            this.uiManager.updateCharacterBackground(this.gameState.player_character);
            this.uiManager.updateParty(this.gameState.party_members);
            this.uiManager.clearNarrative();
            this.uiManager.updateNarrative(this.gameState);
            this.uiManager.updateConversationHistory(this.gameState.conversation_history);

            // Show game screen
            this.uiManager.showScreen('game-screen');

            // Initialize common actions
            this.uiManager.updateCommonActions();

        } catch (error) {
            console.error('Failed to create new game:', error);
            alert('Failed to create new game. Please try again.');
            this.uiManager.showScreen('new-game-screen');
        }
    }

    async handleCommonAction(action) {
        if (!this.sessionId) {
            alert('No active game session');
            return;
        }

        try {
            // Send action to server
            const response = await this.apiService.postAction(this.sessionId, action);

            // Update game state
            this.gameState = response;

            // Update UI
            this.uiManager.updateCharacterSheet(this.gameState.player_character);
            this.uiManager.updateCharacterBackground(this.gameState.player_character);
            this.uiManager.updateParty(this.gameState.party_members);
            this.uiManager.updateNarrative(this.gameState);
            this.uiManager.updateConversationHistory(this.gameState.conversation_history);

        } catch (error) {
            console.error('Failed to process action:', error);
            this.uiManager.updateNarrative('Sorry, I encountered an error processing your action. Please try again.');
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

            // Send action to server
            const response = await this.apiService.postAction(this.sessionId, action);

            // Update game state
            this.gameState = response;

            // Update UI
            this.uiManager.updateCharacterSheet(this.gameState.player_character);
            this.uiManager.updateCharacterBackground(this.gameState.player_character);
            this.uiManager.updateParty(this.gameState.party_members);
            this.uiManager.updateNarrative(this.gameState);
            this.uiManager.updateConversationHistory(this.gameState.conversation_history);

        } catch (error) {
            console.error('Failed to process action:', error);
            this.uiManager.updateNarrative('Sorry, I encountered an error processing your action. Please try again.');
        }
    }

    async handleActionInputFromOption(action) {
        if (!action) return;

        if (!this.sessionId) {
            alert('No active game session');
            return;
        }

        try {
            // Send action to server
            const response = await this.apiService.postAction(this.sessionId, action);

            // Update game state
            this.gameState = response;

            // Update UI
            this.uiManager.updateCharacterSheet(this.gameState.player_character);
            this.uiManager.updateCharacterBackground(this.gameState.player_character);
            this.uiManager.updateParty(this.gameState.party_members);
            this.uiManager.updateNarrative(this.gameState);
            this.uiManager.updateConversationHistory(this.gameState.conversation_history);

        } catch (error) {
            console.error('Failed to process action:', error);
            this.uiManager.updateNarrative('Sorry, I encountered an error processing your action. Please try again.');
        }
    }

    async handleSaveGame() {
        if (!this.sessionId) {
            alert('No active game session to save');
            return;
        }

        try {
            const response = await fetch(`${this.apiService.baseUrl}/${this.sessionId}/save`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            alert('Game saved successfully!');
            console.log('Game saved:', result);
        } catch (error) {
            console.error('Failed to save game:', error);
            alert('Failed to save game. Please try again.');
        }
    }

    async handleShowHistory() {
        if (this.gameState && this.gameState.conversation_history) {
            this.uiManager.updateConversationHistory(this.gameState.conversation_history);
            this.uiManager.showConversationHistory();
        } else {
            alert('No conversation history available');
        }
    }

    handleCloseModals() {
        // Hide all modals
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.classList.add('hidden');
        });
    }

    async handleLoadGame(event) {
        event.preventDefault();

        const sessionId = document.getElementById('load-session-id').value.trim();
        if (!sessionId) {
            alert('Please enter a session ID');
            return;
        }

        try {
            // Show loading screen
            this.uiManager.showScreen('loading-screen');

            // Load game state
            const response = await fetch(`${this.apiService.baseUrl}/load`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ session_id: sessionId })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            this.sessionId = sessionId;
            this.gameState = result;

            // Update UI
            this.uiManager.showSessionId(this.sessionId);
            this.uiManager.updateCharacterSheet(this.gameState.player_character);
            this.uiManager.updateCharacterBackground(this.gameState.player_character);
            this.uiManager.updateParty(this.gameState.party_members);
            this.uiManager.updateConversationHistory(this.gameState.conversation_history);
            this.uiManager.clearNarrative();
            this.uiManager.updateNarrative(this.gameState);

            // Show game screen
            this.uiManager.showScreen('game-screen');

            // Initialize common actions
            this.uiManager.updateCommonActions();

            // Hide load modal
            this.handleCloseModals();

        } catch (error) {
            console.error('Failed to load game:', error);
            alert('Failed to load game. Please check the session ID and try again.');
            this.uiManager.showScreen('game-screen');
        }
    }
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.gameApp = new GameApp();
    console.log('Sword World 2.5 AI GM initialized');
});
