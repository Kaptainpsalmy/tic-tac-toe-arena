// Game state
let gameState = null;

// DOM elements
const boardElement = document.getElementById('board');
const statusElement = document.querySelector('.status');
const resetBtn = document.getElementById('resetBtn');

// Initialize game on load
document.addEventListener('DOMContentLoaded', () => {
    fetchGameState();
    setupEventListeners();
});

function setupEventListeners() {
    resetBtn.addEventListener('click', startNewGame);
}

async function fetchGameState() {
    try {
        const response = await fetch('/api/game-state');
        const data = await response.json();

        if (data.success) {
            gameState = data.game_state;
            renderBoard();
        } else {
            showError('Failed to load game state');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Network error. Please refresh.');
    }
}

async function makeMove(position) {
    try {
        const response = await fetch('/api/move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ position: position })
        });

        const data = await response.json();

        if (data.success) {
            gameState = data.game_state;
            renderBoard();
            statusElement.textContent = data.message;

            // Highlight winning line if game is won
            if (data.winning_line) {
                highlightWinningLine(data.winning_line);
            }
        } else {
            showError(data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to make move');
    }
}

async function startNewGame() {
    try {
        const response = await fetch('/api/new-game', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            gameState = data.game_state;
            renderBoard();
            statusElement.textContent = "Player X's turn";
            removeHighlights();
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to start new game');
    }
}

function renderBoard() {
    if (!gameState) return;

    boardElement.innerHTML = '';
    gameState.board.forEach((cell, index) => {
        const cellElement = document.createElement('div');
        cellElement.classList.add('cell');

        if (cell === 'X') cellElement.classList.add('x');
        if (cell === 'O') cellElement.classList.add('o');

        cellElement.textContent = cell;
        cellElement.dataset.index = index;

        // Only add click handler if game is not over and cell is empty
        if (!gameState.game_over && cell === '') {
            cellElement.addEventListener('click', () => makeMove(index));
            cellElement.style.cursor = 'pointer';
        } else {
            cellElement.style.cursor = 'not-allowed';
        }

        boardElement.appendChild(cellElement);
    });

    // Update status if not already updated by move
    if (!gameState.game_over) {
        statusElement.textContent = `Player ${gameState.current_player}'s turn`;
    } else if (gameState.winner) {
        statusElement.textContent = `🎉 Player ${gameState.winner} wins! 🎉`;
    } else {
        statusElement.textContent = "🤝 It's a draw! 🤝";
    }
}

function highlightWinningLine(winningLine) {
    if (!winningLine) return;

    const cells = document.querySelectorAll('.cell');
    winningLine.forEach(index => {
        cells[index].classList.add('win');
    });
}

function removeHighlights() {
    const cells = document.querySelectorAll('.cell');
    cells.forEach(cell => cell.classList.remove('win'));
}

function showError(message) {
    statusElement.textContent = `❌ ${message}`;
    statusElement.style.color = '#ef4444';
    setTimeout(() => {
        statusElement.style.color = '';
        if (gameState && !gameState.game_over) {
            statusElement.textContent = `Player ${gameState.current_player}'s turn`;
        }
    }, 3000);
}

// Keyboard support for accessibility
document.addEventListener('keydown', (e) => {
    // Press 'r' to reset game
    if (e.key.toLowerCase() === 'r') {
        startNewGame();
    }

    // Number keys 1-9 for moves (accessibility feature)
    if (e.key >= '1' && e.key <= '9' && gameState && !gameState.game_over) {
        const position = parseInt(e.key) - 1;
        if (gameState.board[position] === '') {
            makeMove(position);
        }
    }
});