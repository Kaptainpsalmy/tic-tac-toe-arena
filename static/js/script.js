// Wait for DOM to load
document.addEventListener('DOMContentLoaded', () => {
    const boardElement = document.getElementById('board');
    const statusElement = document.querySelector('.status');
    const resetBtn = document.getElementById('resetBtn');

    // Create empty board
    let board = ['', '', '', '', '', '', '', '', ''];
    let currentPlayer = 'X';
    let gameActive = true;

    // Initialize board UI
    function renderBoard() {
        boardElement.innerHTML = '';
        board.forEach((cell, index) => {
            const cellElement = document.createElement('div');
            cellElement.classList.add('cell');
            if (cell === 'X') cellElement.classList.add('x');
            if (cell === 'O') cellElement.classList.add('o');
            cellElement.textContent = cell;
            cellElement.dataset.index = index;
            cellElement.addEventListener('click', handleCellClick);
            boardElement.appendChild(cellElement);
        });
    }

    // Handle cell clicks
    function handleCellClick(e) {
        const index = e.target.dataset.index;

        if (!gameActive || board[index] !== '') return;

        // Update board
        board[index] = currentPlayer;
        checkGameStatus();
        currentPlayer = currentPlayer === 'X' ? 'O' : 'X';
        renderBoard();
    }

    // Check win/draw
    function checkGameStatus() {
        const winPatterns = [
            [0,1,2], [3,4,5], [6,7,8], // rows
            [0,3,6], [1,4,7], [2,5,8], // columns
            [0,4,8], [2,4,6] // diagonals
        ];

        for (let pattern of winPatterns) {
            const [a,b,c] = pattern;
            if (board[a] && board[a] === board[b] && board[a] === board[c]) {
                gameActive = false;
                statusElement.textContent = `🎉 Player ${board[a]} wins! 🎉`;
                return;
            }
        }

        if (!board.includes('')) {
            gameActive = false;
            statusElement.textContent = "🤝 It's a draw! 🤝";
        } else {
            statusElement.textContent = `Player ${currentPlayer}'s turn`;
        }
    }

    // Reset game
    function resetGame() {
        board = ['', '', '', '', '', '', '', '', ''];
        currentPlayer = 'X';
        gameActive = true;
        statusElement.textContent = "Player X's turn";
        renderBoard();
    }

    // Event listeners
    resetBtn.addEventListener('click', resetGame);

    // Initial render
    renderBoard();
    statusElement.textContent = "Player X's turn";
});