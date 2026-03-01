// Game state
let gameState = null;
let scores = { X: 0, O: 0 };
let soundEnabled = true;
let animationsEnabled = true;
let aiQuotesEnabled = true;
let currentMode = '2p';

// AI Game State
let aiMode = false;
let aiDifficulty = 'medium';
let aiStats = {
    aiWins: 0,
    humanWins: 0,
    streak: 0,
    totalGames: 0
};

// AI Personalities
const aiPersonalities = {
    easy: {
        name: '🤖 Novice Bot',
        title: 'Novice AI',
        color: '#22c55e',
        description: 'Makes random moves - Perfect for beginners!',
        quotes: {
            thinking: [
                "Hmm, where should I go?",
                "This is fun!",
                "Learning the game...",
                "Random move incoming!",
                "I hope this works!"
            ],
            move: [
                "Here goes nothing!",
                "Random choice!",
                "Why not here?",
                "Looks good to me!",
                "Beginner's luck!"
            ],
            win: [
                "Wow! I won?",
                "Beginner's luck!",
                "Did I just win?",
                "This is amazing!",
                "I'm learning fast!"
            ],
            lose: [
                "Good game!",
                "You're too good!",
                "I'll get better!",
                "Teach me your ways!",
                "Next time I'll win!"
            ]
        }
    },
    medium: {
        name: '🎯 Tactical AI',
        title: 'Tactical AI',
        color: '#f59e0b',
        description: 'Blocks your wins and takes center - Getting tricky!',
        quotes: {
            thinking: [
                "Analyzing patterns...",
                "I see your strategy",
                "Interesting move...",
                "Calculating...",
                "You're good!"
            ],
            move: [
                "Blocking your win!",
                "Taking control!",
                "Strategic move!",
                "Setting up...",
                "Good counter!"
            ],
            win: [
                "Calculated!",
                "Strategy prevails!",
                "I predicted that!",
                "Victory!",
                "Tactical win!"
            ],
            lose: [
                "You outsmarted me!",
                "Well played!",
                "Impressive strategy!",
                "I'll study this game",
                "Rematch?"
            ]
        }
    },
    hard: {
        name: '🧠 Master AI',
        title: 'Master AI',
        color: '#ef4444',
        description: 'Uses minimax strategy - Quite challenging!',
        quotes: {
            thinking: [
                "Processing minimax...",
                "Evaluating positions...",
                "Deep calculation...",
                "Optimal move found",
                "You're challenging"
            ],
            move: [
                "Optimal move",
                "Best response",
                "Maximizing advantage",
                "Minimizing your options",
                "Perfect play"
            ],
            win: [
                "Masterful victory!",
                "Optimal play wins!",
                "I saw that coming",
                "Checkmate!",
                "Superior strategy"
            ],
            lose: [
                "You beat the master!",
                "Impressive!",
                "Well calculated!",
                "You're a pro!",
                "Amazing game!"
            ]
        }
    },
    expert: {
        name: '👑 Grandmaster AI',
        title: 'Grandmaster AI',
        color: '#8b5cf6',
        description: 'Unbeatable - Can you force a draw?',
        quotes: {
            thinking: [
                "Perfect calculation...",
                "No mistakes allowed",
                "Analyzing all possibilities",
                "Victory is certain",
                "You cannot win"
            ],
            move: [
                "Perfect move",
                "Unbeatable strategy",
                "Your move is futile",
                "I've seen this before",
                "Error-free play"
            ],
            win: [
                "As expected",
                "Victory is inevitable",
                "I am unbeatable",
                "Another win",
                "Perfect play prevails"
            ],
            lose: [
                "IMPOSSIBLE!",
                "How did you...",
                "This cannot be!",
                "You found a flaw?",
                "I need recalibration"
            ]
        }
    }
};

// ============ DOM ELEMENTS ============
const boardElement = document.getElementById('board');
const statusText = document.querySelector('.status-text');
const turnIndicator = document.querySelector('.turn-indicator');
const moveCounter = document.getElementById('moveCounter');
const scoreX = document.getElementById('scoreX');
const scoreO = document.getElementById('scoreO');
const resetBtn = document.getElementById('resetBtn');
const undoBtn = document.getElementById('undoBtn');
const settingsBtn = document.getElementById('settingsBtn');
const winningOverlay = document.getElementById('winningOverlay');
const winnerMessage = document.getElementById('winnerMessage');
const playAgainOverlay = document.getElementById('playAgainFromOverlay');
const moveHistoryList = document.getElementById('historyList');
const settingsModal = document.getElementById('settingsModal');
const closeModal = document.getElementById('closeModal');
const soundToggle = document.getElementById('soundToggle');
const themeToggle = document.getElementById('themeToggle');
const animationsToggle = document.getElementById('animationsToggle');
const modeButtons = document.querySelectorAll('.mode-btn');
const clearHistoryBtn = document.getElementById('clearHistory');
const confettiCanvas = document.getElementById('confetti-canvas');

// AI DOM elements
const aiThinkingIndicator = document.getElementById('aiThinking');
const aiProgressBar = document.getElementById('aiProgressBar');
const aiStatsCard = document.getElementById('aiStatsCard');
const aiWinsEl = document.getElementById('aiWins');
const humanWinsEl = document.getElementById('humanWins');
const aiWinRateEl = document.getElementById('aiWinRate');
const aiStreakEl = document.getElementById('aiStreak');
const resetAIStatsBtn = document.getElementById('resetAIStats');
const aiNameEl = document.getElementById('aiName');
const aiQuoteEl = document.getElementById('aiQuote');
const aiDescriptionEl = document.getElementById('aiDescription');
const aiQuotesToggle = document.getElementById('aiQuotesToggle');

// Toast container
const toastContainer = document.getElementById('toastContainer');

// Save settings button
const saveSettingsBtn = document.getElementById('saveSettings');

// ============ UTILITY FUNCTIONS ============

// Notification system
function showNotification(message, type = 'info') {
    if (!toastContainer) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        info: 'fa-info-circle',
        warning: 'fa-exclamation-triangle'
    };

    toast.innerHTML = `
        <i class="fas ${icons[type] || icons.info}"></i>
        <span>${message}</span>
    `;

    toastContainer.appendChild(toast);

    setTimeout(() => toast.classList.add('show'), 10);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Sound effects
function playSound(type) {
    if (!soundEnabled) return;

    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    switch(type) {
        case 'move':
            oscillator.frequency.value = 800;
            gainNode.gain.value = 0.1;
            oscillator.start();
            oscillator.stop(audioContext.currentTime + 0.1);
            break;
        case 'win':
            oscillator.frequency.value = 600;
            gainNode.gain.value = 0.2;
            oscillator.start();
            oscillator.frequency.value = 800;
            oscillator.stop(audioContext.currentTime + 0.3);
            break;
        case 'error':
            oscillator.frequency.value = 200;
            gainNode.gain.value = 0.1;
            oscillator.start();
            oscillator.stop(audioContext.currentTime + 0.1);
            break;
        case 'newGame':
            oscillator.frequency.value = 400;
            gainNode.gain.value = 0.1;
            oscillator.start();
            oscillator.frequency.value = 600;
            oscillator.stop(audioContext.currentTime + 0.2);
            break;
        case 'click':
            oscillator.frequency.value = 600;
            gainNode.gain.value = 0.05;
            oscillator.start();
            oscillator.stop(audioContext.currentTime + 0.05);
            break;
        case 'undo':
            oscillator.frequency.value = 300;
            gainNode.gain.value = 0.1;
            oscillator.start();
            oscillator.frequency.value = 200;
            oscillator.stop(audioContext.currentTime + 0.1);
            break;
    }
}

// Confetti effect
function initConfetti() {
    if (!confettiCanvas) return;

    const ctx = confettiCanvas.getContext('2d');
    let particles = [];
    let animationFrame = null;

    function createParticles() {
        for (let i = 0; i < 50; i++) {
            particles.push({
                x: Math.random() * window.innerWidth,
                y: Math.random() * window.innerHeight - window.innerHeight,
                size: Math.random() * 5 + 2,
                speedY: Math.random() * 3 + 2,
                speedX: Math.random() * 2 - 1,
                color: `hsl(${Math.random() * 360}, 50%, 50%)`
            });
        }
    }

    function animateParticles() {
        ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);

        particles.forEach((p, index) => {
            p.y += p.speedY;
            p.x += p.speedX;

            ctx.fillStyle = p.color;
            ctx.fillRect(p.x, p.y, p.size, p.size);

            if (p.y > window.innerHeight) {
                particles.splice(index, 1);
            }
        });

        if (particles.length > 0) {
            animationFrame = requestAnimationFrame(animateParticles);
        } else {
            if (animationFrame) {
                cancelAnimationFrame(animationFrame);
            }
        }
    }

    window.triggerConfetti = () => {
        if (!animationsEnabled) return;
        if (animationFrame) {
            cancelAnimationFrame(animationFrame);
        }
        particles = [];
        createParticles();
        animateParticles();
    };
}

// Theme toggle
function toggleTheme() {
    document.body.classList.toggle('light-theme');
    const isLight = document.body.classList.contains('light-theme');
    if (themeToggle) {
        themeToggle.checked = !isLight;
    }
}

// Clear highlights
function clearHighlights() {
    const cells = document.querySelectorAll('.cell');
    cells.forEach(cell => {
        cell.classList.remove('win');
        cell.style.animation = '';
    });
}

// Update scores
function updateScores(winner) {
    if (winner === 'X') {
        scores.X++;
        if (scoreX) scoreX.textContent = scores.X;
    } else if (winner === 'O') {
        scores.O++;
        if (scoreO) scoreO.textContent = scores.O;
    }
}

// Show winning overlay
function showWinningOverlay(winner) {
    if (!winnerMessage || !winningOverlay) return;

    if (winner === 'draw') {
        winnerMessage.textContent = "It's a Draw!";
    } else {
        winnerMessage.textContent = `Player ${winner} Wins!`;
    }
    winningOverlay.classList.add('show');
}

// Update move history
function updateMoveHistory() {
    if (!gameState || !moveHistoryList) return;

    moveHistoryList.innerHTML = '';
    gameState.move_history.forEach(move => {
        const moveItem = document.createElement('div');
        moveItem.classList.add('move-item', `${move.player.toLowerCase()}-move`);

        const row = Math.floor(move.position / 3) + 1;
        const col = (move.position % 3) + 1;

        moveItem.innerHTML = `
            <span>${move.player}</span>
            <span>(${row},${col})</span>
        `;
        moveHistoryList.appendChild(moveItem);
    });
}

// Clear move history
function clearMoveHistory() {
    if (moveHistoryList) {
        moveHistoryList.innerHTML = '';
    }
    showNotification('History cleared', 'info');
}

// Highlight winning line
function highlightWinningLine(winningLine) {
    if (!winningLine) return;

    const cells = document.querySelectorAll('.cell');
    winningLine.forEach(index => {
        cells[index].classList.add('win');
        if (animationsEnabled) {
            cells[index].style.animation = 'winPulse 1s ease infinite';
        }
    });
}

// ============ AI FUNCTIONS ============

function getAIName(difficulty) {
    const names = {
        'easy': 'Novice AI',
        'medium': 'Tactical AI',
        'hard': 'Master AI',
        'expert': 'Grandmaster AI'
    };
    return names[difficulty] || 'AI Opponent';
}

function updateAIPersonality(difficulty) {
    const personality = aiPersonalities[difficulty] || aiPersonalities.medium;
    if (aiNameEl) {
        aiNameEl.textContent = personality.title;
        aiNameEl.style.color = personality.color;
    }
    if (aiDescriptionEl) {
        aiDescriptionEl.textContent = personality.description;
    }
}

function getRandomQuote(difficulty, type) {
    const personality = aiPersonalities[difficulty] || aiPersonalities.medium;
    const quotes = personality.quotes[type] || personality.quotes.thinking;
    return quotes[Math.floor(Math.random() * quotes.length)];
}

function highlightAIMove(position) {
    const cells = document.querySelectorAll('.cell');
    if (cells[position]) {
        cells[position].classList.add('ai-move-highlight');
        setTimeout(() => {
            cells[position].classList.remove('ai-move-highlight');
        }, 500);
    }
}

function updateAIStatsUI() {
    if (aiWinsEl) {
        aiWinsEl.textContent = aiStats.aiWins;
        humanWinsEl.textContent = aiStats.humanWins;

        const total = aiStats.aiWins + aiStats.humanWins;
        const winRate = total > 0 ? Math.round((aiStats.aiWins / total) * 100) : 0;
        aiWinRateEl.textContent = `${winRate}%`;

        aiStreakEl.textContent = aiStats.streak;

        if (aiStats.streak >= 3) {
            aiStreakEl.style.color = '#ef4444';
        } else if (aiStats.streak >= 1) {
            aiStreakEl.style.color = '#f59e0b';
        } else {
            aiStreakEl.style.color = '#22c55e';
        }
    }
}

function saveAIStats() {
    localStorage.setItem('aiStats', JSON.stringify(aiStats));
}

function loadAIStats() {
    const saved = localStorage.getItem('aiStats');
    if (saved) {
        try {
            aiStats = JSON.parse(saved);
            updateAIStatsUI();
        } catch (e) {
            console.error('Error loading AI stats:', e);
        }
    }
}

function updateAIStats(winner) {
    aiStats.totalGames++;

    if (winner === 'O') {
        aiStats.aiWins++;
        aiStats.streak++;
    } else if (winner === 'X') {
        aiStats.humanWins++;
        aiStats.streak = 0;
    } else {
        aiStats.streak = 0;
    }

    updateAIStatsUI();
    saveAIStats();
}

function resetAIStats() {
    if (confirm('Are you sure you want to reset AI statistics?')) {
        aiStats = {
            aiWins: 0,
            humanWins: 0,
            streak: 0,
            totalGames: 0
        };
        updateAIStatsUI();
        saveAIStats();
        showNotification('AI statistics reset', 'success');
    }
}

async function fetchAIPersonality(difficulty) {
    try {
        const response = await fetch('/api/ai-personality', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ difficulty })
        });

        const data = await response.json();
        if (data.success && aiQuoteEl) {
            aiQuoteEl.textContent = `"${getRandomQuote(difficulty, 'thinking')}"`;
        }
    } catch (error) {
        console.error('Error fetching AI personality:', error);
    }
}

// ============ CORE GAME FUNCTIONS ============

// Render board
function renderBoard() {
    if (!boardElement || !gameState) return;

    boardElement.innerHTML = '';
    gameState.board.forEach((cell, index) => {
        const cellElement = document.createElement('div');
        cellElement.classList.add('cell');

        if (cell === 'X') {
            cellElement.classList.add('x');
            cellElement.innerHTML = '<i class="fas fa-times"></i>';
        } else if (cell === 'O') {
            cellElement.classList.add('o');
            cellElement.innerHTML = '<i class="far fa-circle"></i>';
        }

        cellElement.dataset.index = index;

        // SIMPLE: Only allow clicks when it's human's turn and game not over
        if (!gameState.game_over) {
            if (aiMode) {
                // In AI mode: only allow clicks when it's human's turn (X)
                if (gameState.current_player === 'X' && cell === '') {
                    // In renderBoard function, update the click handler:
                    cellElement.addEventListener('click', () => makeMove(index, false));
                    cellElement.style.cursor = 'pointer';
                } else {
                    cellElement.style.cursor = 'default';
                }
            } else {
                // 2-player mode: allow clicks on empty cells
                if (cell === '') {
                    // In renderBoard function, update the click handler:
                    cellElement.addEventListener('click', () => makeMove(index, false));
                    cellElement.style.cursor = 'pointer';
                } else {
                    cellElement.style.cursor = 'default';
                }
            }
        } else {
            cellElement.style.cursor = 'default';
        }

        if (animationsEnabled && cell) {
            cellElement.style.animation = 'popIn 0.3s ease';
        }

        boardElement.appendChild(cellElement);
    });
}

// Update UI
function updateUI() {
    if (!gameState) return;

    renderBoard();

    if (gameState.game_over) {
        if (gameState.winner) {
            if (statusText) statusText.textContent = `🎉 Player ${gameState.winner} Wins! 🎉`;
            if (turnIndicator) turnIndicator.style.background = gameState.winner === 'X' ? '#22c55e' : '#f59e0b';
        } else {
            if (statusText) statusText.textContent = "🤝 Game Draw! 🤝";
            if (turnIndicator) turnIndicator.style.background = '#9ca3af';
        }
        if (undoBtn) undoBtn.disabled = false;
    } else {
        if (statusText) statusText.textContent = `Player ${gameState.current_player}'s turn`;
        if (turnIndicator) turnIndicator.style.background = gameState.current_player === 'X' ? '#22c55e' : '#f59e0b';
        if (undoBtn) undoBtn.disabled = gameState.move_history.length === 0;
    }

    if (moveCounter) {
        moveCounter.innerHTML = `<i class="fas fa-history"></i> Moves: ${gameState.move_history.length}`;
    }

    document.querySelectorAll('.player-card').forEach(card => card.classList.remove('active'));
    if (!gameState.game_over) {
        const player = gameState.current_player.toLowerCase();
        const activeCard = document.querySelector(`.player-${player}`);
        if (activeCard) {
            activeCard.classList.add('active');
        }
    }

    updateMoveHistory();
}

// ============ API FUNCTIONS ============

async function fetchGameState() {
    try {
        const response = await fetch('/api/game-state');
        const data = await response.json();

        if (data.success) {
            gameState = data.game_state;
            updateUI();
            loadSettings();

            // Check if it's AI's turn
            if (aiMode && !gameState.game_over && gameState.current_player === 'O') {
                setTimeout(() => makeAIMove(), 100);
            }
        } else {
            showNotification('Failed to load game state', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Failed to load game', 'error');
    }
}

async function makeMove(position, isAIMove = false) {
    console.log("🎮 makeMove called with position:", position, "isAIMove:", isAIMove);
    console.log("Current game state:", gameState);

    // Prevent moves if game is over
    if (gameState.game_over) {
        console.log("❌ Game is over, cannot move");
        return;
    }

    // FIX: Allow AI moves even when it's AI's turn
    if (aiMode && gameState.current_player === 'O' && !isAIMove) {
        console.log("❌ It's AI's turn, human cannot play");
        return;
    }

    try {
        const response = await fetch('/api/move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ position })
        });

        const data = await response.json();
        console.log("Move response:", data);

        if (data.success) {
            gameState = data.game_state;
            playSound('move');
            updateUI();

            if (data.winning_line) {
                highlightWinningLine(data.winning_line);
                playSound('win');
                showWinningOverlay(gameState.winner);
                updateScores(gameState.winner);
                if (window.triggerConfetti) window.triggerConfetti();

                if (aiMode) {
                    updateAIStats(gameState.winner);
                }
            } else if (gameState.game_over) {
                playSound('draw');
                showWinningOverlay('draw');

                if (aiMode) {
                    updateAIStats(null);
                }
            }
            // Trigger AI move if it's AI's turn and not already an AI move
            else if (aiMode && gameState.current_player === 'O' && !isAIMove) {
                console.log("Triggering AI move from makeMove");
                setTimeout(() => makeAIMove(), 100);
            }
        } else {
            showNotification(data.message, 'error');
            playSound('error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Failed to make move', 'error');
    }
}
async function makeAIMove() {
    console.log("🔍 AI move function called");
    console.log("aiMode:", aiMode);
    console.log("game_over:", gameState?.game_over);
    console.log("current_player:", gameState?.current_player);

    if (!aiMode || gameState.game_over) {
        console.log("❌ AI move cancelled - conditions not met");
        return;
    }

    // Check if it's AI's turn
    if (gameState.current_player !== 'O') {
        console.log("❌ Not AI's turn - current player is:", gameState.current_player);
        return;
    }

    console.log("🤖 AI is making its move...");

    try {
        console.log("Sending request to /api/ai-move with:", {
            difficulty: aiDifficulty,
            board: gameState.board,
            ai_player: 'O'
        });

        const response = await fetch('/api/ai-move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                difficulty: aiDifficulty,
                board: gameState.board,
                ai_player: 'O'
            })
        });

        console.log("📡 Response status:", response.status);
        const data = await response.json();
        console.log("📦 Response data:", data);

        if (data.success && data.position !== -1) {
            console.log(`✅ AI chose position: ${data.position}`);
            highlightAIMove(data.position);

            if (aiQuotesEnabled && aiQuoteEl) {
                aiQuoteEl.textContent = `"${getRandomQuote(aiDifficulty, 'move')}"`;
            }

            // FIX: Pass true to indicate this is an AI move
            console.log("🎯 Calling makeMove with position:", data.position, "as AI move");
            await makeMove(data.position, true);
            console.log("✅ AI move completed");
        } else {
            console.error('❌ AI move failed:', data);
            showNotification('AI failed to move', 'error');
        }
    } catch (error) {
        console.error('❌ AI move error:', error);
        showNotification('AI failed to move', 'error');
    }
}async function startNewGame() {
    try {
        const response = await fetch('/api/new-game', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            gameState = data.game_state;
            if (winningOverlay) winningOverlay.classList.remove('show');
            playSound('newGame');
            updateUI();
            clearHighlights();
            showNotification('New game started!', 'success');

            // Check if AI goes first
            if (aiMode && gameState.current_player === 'O') {
                setTimeout(() => makeAIMove(), 100);
            }

            if (aiQuoteEl) {
                aiQuoteEl.textContent = '';
            }
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Failed to start new game', 'error');
    }
}

async function undoMove() {
    try {
        const response = await fetch('/api/undo', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            gameState = data.game_state;
            playSound('undo');
            updateUI();
            clearHighlights();
            if (winningOverlay) winningOverlay.classList.remove('show');

            // Check if it's AI's turn after undo
            if (aiMode && gameState.current_player === 'O' && !gameState.game_over) {
                setTimeout(() => makeAIMove(), 100);
            }
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Failed to undo move', 'error');
    }
}

// ============ SETTINGS FUNCTIONS ============

function saveSettings() {
    const settings = {
        soundEnabled,
        animationsEnabled,
        aiQuotesEnabled,
        theme: document.body.classList.contains('light-theme') ? 'light' : 'dark'
    };

    localStorage.setItem('gameSettings', JSON.stringify(settings));
    if (settingsModal) settingsModal.classList.remove('show');
    showToast('Settings saved!', 'success');
}

function loadSettings() {
    const saved = localStorage.getItem('gameSettings');
    if (saved) {
        try {
            const settings = JSON.parse(saved);

            if (settings.soundEnabled !== undefined) {
                soundEnabled = settings.soundEnabled;
                if (soundToggle) soundToggle.checked = soundEnabled;
            }

            if (settings.animationsEnabled !== undefined) {
                animationsEnabled = settings.animationsEnabled;
                if (animationsToggle) animationsToggle.checked = animationsEnabled;
            }

            if (settings.aiQuotesEnabled !== undefined) {
                aiQuotesEnabled = settings.aiQuotesEnabled;
                if (aiQuotesToggle) aiQuotesToggle.checked = aiQuotesEnabled;
            }

            if (settings.theme === 'light') {
                document.body.classList.add('light-theme');
                if (themeToggle) themeToggle.checked = false;
            }
        } catch (e) {
            console.error('Error loading settings:', e);
        }
    }
}

// Toast notification
function showToast(message, type = 'info') {
    showNotification(message, type);
}

// ============ EVENT LISTENERS ============

function setupEventListeners() {
    if (resetBtn) resetBtn.addEventListener('click', startNewGame);
    if (undoBtn) undoBtn.addEventListener('click', undoMove);
    if (settingsBtn) settingsBtn.addEventListener('click', () => settingsModal.classList.add('show'));
    if (closeModal) closeModal.addEventListener('click', () => settingsModal.classList.remove('show'));
    if (playAgainOverlay) playAgainOverlay.addEventListener('click', startNewGame);
    if (clearHistoryBtn) clearHistoryBtn.addEventListener('click', clearMoveHistory);

    // Settings toggles
    if (soundToggle) {
        soundToggle.addEventListener('change', (e) => soundEnabled = e.target.checked);
    }
    if (themeToggle) {
        themeToggle.addEventListener('change', toggleTheme);
    }
    if (animationsToggle) {
        animationsToggle.addEventListener('change', (e) => animationsEnabled = e.target.checked);
    }
    if (aiQuotesToggle) {
        aiQuotesToggle.addEventListener('change', (e) => aiQuotesEnabled = e.target.checked);
    }

    // Save settings button
    if (saveSettingsBtn) {
        saveSettingsBtn.addEventListener('click', saveSettings);
    }

    // Mode buttons with AI support
    modeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            modeButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const mode = btn.dataset.mode;
            currentMode = mode;

            if (mode === '2p') {
                aiMode = false;
                if (aiStatsCard) aiStatsCard.style.display = 'none';
                showNotification('2 Player Mode activated', 'info');
            } else {
                aiMode = true;
                aiDifficulty = mode.replace('ai-', '');
                if (aiStatsCard) aiStatsCard.style.display = 'block';
                updateAIPersonality(aiDifficulty);
                fetchAIPersonality(aiDifficulty);
                showNotification(`${getAIName(aiDifficulty)} mode activated - You are X, AI is O`, 'info');
            }

            startNewGame();
            playSound('click');
        });
    });

    // AI Stats reset
    if (resetAIStatsBtn) {
        resetAIStatsBtn.addEventListener('click', resetAIStats);
    }

    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === settingsModal) {
            settingsModal.classList.remove('show');
        }
        if (e.target === infoModal) {
            infoModal.classList.remove('show');
        }
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.key.toLowerCase() === 'r') startNewGame();
        if (e.key.toLowerCase() === 'u' && undoBtn && !undoBtn.disabled) undoMove();
        if (e.key === 'Escape') {
            if (settingsModal) settingsModal.classList.remove('show');
            if (infoModal) infoModal.classList.remove('show');
        }
    });
}

// ============ INITIALIZATION ============

// Add CSS styles
const style = document.createElement('style');
style.textContent = `
    @keyframes popIn {
        0% { transform: scale(0); opacity: 0; }
        80% { transform: scale(1.1); }
        100% { transform: scale(1); opacity: 1; }
    }

    @keyframes winPulse {
        0%, 100% { transform: scale(1); box-shadow: 0 0 20px currentColor; }
        50% { transform: scale(1.05); box-shadow: 0 0 40px currentColor; }
    }

    .ai-move-highlight {
        animation: aiThinkPulse 0.5s ease;
    }

    @keyframes aiThinkPulse {
        0%, 100% { box-shadow: 0 0 0 0 #22c55e; }
        50% { box-shadow: 0 0 30px 10px #22c55e; }
    }

    .toast-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 10000;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }

    .toast {
        background: #1f2937;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        display: flex;
        align-items: center;
        gap: 0.8rem;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
        transform: translateX(400px);
        transition: transform 0.3s ease;
        border-left: 4px solid #22c55e;
        min-width: 250px;
    }

    .toast.show {
        transform: translateX(0);
    }

    .toast.success { border-left-color: #22c55e; }
    .toast.error { border-left-color: #ef4444; }
    .toast.info { border-left-color: #3b82f6; }
    .toast.warning { border-left-color: #f59e0b; }

    .toast i {
        font-size: 1.2rem;
    }

    .toast.success i { color: #22c55e; }
    .toast.error i { color: #ef4444; }
    .toast.info i { color: #3b82f6; }
    .toast.warning i { color: #f59e0b; }

    .light-theme {
        background: #f8fafc;
    }

    .light-theme .container {
        background: white;
        color: #1f2937;
    }
`;
document.head.appendChild(style);

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    fetchGameState();
    setupEventListeners();
    initConfetti();
    loadAIPreferences();
    loadAIStats();
});

// Load AI preferences
function loadAIPreferences() {
    const saved = localStorage.getItem('aiPrefs');
    if (saved) {
        try {
            const prefs = JSON.parse(saved);
            aiQuotesEnabled = prefs.aiQuotesEnabled !== undefined ? prefs.aiQuotesEnabled : true;
            if (aiQuotesToggle) aiQuotesToggle.checked = aiQuotesEnabled;
        } catch (e) {
            console.error('Error loading AI prefs:', e);
        }
    }
}

// Save AI preferences
function saveAIPreferences() {
    const prefs = {
        aiQuotesEnabled,
        aiDifficulty
    };
    localStorage.setItem('aiPrefs', JSON.stringify(prefs));
}

// Export for debugging
window.debug = {
    getGameState: () => gameState,
    getAIStats: () => aiStats,
    toggleAIMode: () => {
        aiMode = !aiMode;
        showNotification(`AI Mode: ${aiMode ? 'ON' : 'OFF'}`, 'info');
    }
};