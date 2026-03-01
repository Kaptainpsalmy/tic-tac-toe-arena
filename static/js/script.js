// Game state
let gameState = null;
let scores = { X: 0, O: 0 };
let soundEnabled = true;
let animationsEnabled = true;
let currentMode = '2p';

// DOM elements
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

// Initialize game
document.addEventListener('DOMContentLoaded', () => {
    fetchGameState();
    setupEventListeners();
    initConfetti();
});

function setupEventListeners() {
    resetBtn.addEventListener('click', startNewGame);
    undoBtn.addEventListener('click', undoMove);
    settingsBtn.addEventListener('click', () => settingsModal.classList.add('show'));
    closeModal.addEventListener('click', () => settingsModal.classList.remove('show'));
    playAgainOverlay.addEventListener('click', startNewGame);
    clearHistoryBtn.addEventListener('click', clearMoveHistory);

    // Settings toggles
    soundToggle.addEventListener('change', (e) => soundEnabled = e.target.checked);
    themeToggle.addEventListener('change', toggleTheme);
    animationsToggle.addEventListener('change', (e) => animationsEnabled = e.target.checked);

    // Mode buttons
    modeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            modeButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentMode = btn.dataset.mode;
            startNewGame();
            playSound('click');
        });
    });

    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === settingsModal) {
            settingsModal.classList.remove('show');
        }
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.key.toLowerCase() === 'r') startNewGame();
        if (e.key.toLowerCase() === 'u' && !undoBtn.disabled) undoMove();
        if (e.key === 'Escape') settingsModal.classList.remove('show');
    });
}

async function fetchGameState() {
    try {
        const response = await fetch('/api/game-state');
        const data = await response.json();

        if (data.success) {
            gameState = data.game_state;
            updateUI();
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Failed to load game', 'error');
    }
}

async function makeMove(position) {
    try {
        const response = await fetch('/api/move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ position })
        });

        const data = await response.json();

        if (data.success) {
            gameState = data.game_state;
            playSound('move');
            updateUI();

            if (data.winning_line) {
                highlightWinningLine(data.winning_line);
                playSound('win');
                showWinningOverlay(gameState.winner);
                updateScores(gameState.winner);
                triggerConfetti();
            } else if (gameState.game_over) {
                playSound('draw');
                showWinningOverlay('draw');
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

async function startNewGame() {
    try {
        const response = await fetch('/api/new-game', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            gameState = data.game_state;
            winningOverlay.classList.remove('show');
            playSound('newGame');
            updateUI();
            clearHighlights();
            showNotification('New game started!', 'success');
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
            winningOverlay.classList.remove('show');
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

function updateUI() {
    if (!gameState) return;

    // Render board
    renderBoard();

    // Update status
    if (gameState.game_over) {
        if (gameState.winner) {
            statusText.textContent = `🎉 Player ${gameState.winner} Wins! 🎉`;
            turnIndicator.style.background = gameState.winner === 'X' ? '#22c55e' : '#f59e0b';
        } else {
            statusText.textContent = "🤝 Game Draw! 🤝";
            turnIndicator.style.background = '#9ca3af';
        }
        undoBtn.disabled = false;
    } else {
        statusText.textContent = `Player ${gameState.current_player}'s turn`;
        turnIndicator.style.background = gameState.current_player === 'X' ? '#22c55e' : '#f59e0b';
        undoBtn.disabled = gameState.move_history.length === 0;
    }

    // Update move counter
    moveCounter.innerHTML = `<i class="fas fa-history"></i> Moves: ${gameState.move_history.length}`;

    // Update active player card
    document.querySelectorAll('.player-card').forEach(card => card.classList.remove('active'));
    if (!gameState.game_over) {
        document.querySelector(`.player-${gameState.current_player.toLowerCase()}`).classList.add('active');
    }

    // Update move history
    updateMoveHistory();
}

function renderBoard() {
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

        if (!gameState.game_over && cell === '') {
            cellElement.addEventListener('click', () => makeMove(index));
            cellElement.style.cursor = 'pointer';
        } else {
            cellElement.style.cursor = 'default';
        }

        // Add animation class if enabled
        if (animationsEnabled && cell) {
            cellElement.style.animation = 'popIn 0.3s ease';
        }

        boardElement.appendChild(cellElement);
    });
}

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

function clearHighlights() {
    const cells = document.querySelectorAll('.cell');
    cells.forEach(cell => {
        cell.classList.remove('win');
        cell.style.animation = '';
    });
}

function showWinningOverlay(winner) {
    if (winner === 'draw') {
        winnerMessage.textContent = "It's a Draw!";
    } else {
        winnerMessage.textContent = `Player ${winner} Wins!`;
    }
    winningOverlay.classList.add('show');
}

function updateScores(winner) {
    if (winner === 'X') {
        scores.X++;
        scoreX.textContent = scores.X;
    } else if (winner === 'O') {
        scores.O++;
        scoreO.textContent = scores.O;
    }
}

function updateMoveHistory() {
    if (!gameState) return;

    moveHistoryList.innerHTML = '';
    gameState.move_history.forEach(move => {
        const moveItem = document.createElement('div');
        moveItem.classList.add('move-item', `${move.player.toLowerCase()}-move`);

        // Convert position to grid notation (1-9)
        const row = Math.floor(move.position / 3) + 1;
        const col = (move.position % 3) + 1;

        moveItem.innerHTML = `
            <span>${move.player}</span>
            <span>(${row},${col})</span>
        `;
        moveHistoryList.appendChild(moveItem);
    });
}

function clearMoveHistory() {
    moveHistoryList.innerHTML = '';
    showNotification('History cleared', 'info');
}

function toggleTheme() {
    document.body.classList.toggle('light-theme');
}

// Sound effects (using Web Audio API)
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
    }
}

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas ${type === 'error' ? 'fa-exclamation-circle' : type === 'success' ? 'fa-check-circle' : 'fa-info-circle'}"></i>
        <span>${message}</span>
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('show');
    }, 100);

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Confetti effect
function initConfetti() {
    const ctx = confettiCanvas.getContext('2d');
    let particles = [];

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
            requestAnimationFrame(animateParticles);
        }
    }

    window.triggerConfetti = () => {
        if (!animationsEnabled) return;
        particles = [];
        createParticles();
        animateParticles();
    };
}

// Add CSS animations
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

    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 2rem;
        border-radius: 10px;
        color: white;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        transform: translateX(400px);
        transition: transform 0.3s ease;
        z-index: 10000;
    }

    .notification.show {
        transform: translateX(0);
    }

    .notification.error { background: #ef4444; }
    .notification.success { background: #22c55e; }
    .notification.info { background: #3b82f6; }

    .light-theme {
        background: #f8fafc;
    }

    .light-theme .container {
        background: white;
        color: #1f2937;
    }
`;
document.head.appendChild(style);