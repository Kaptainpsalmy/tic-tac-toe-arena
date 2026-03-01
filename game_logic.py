class TicTacToe:
    def __init__(self):
        self.board = [''] * 9
        self.current_player = 'X'
        self.winner = None
        self.game_over = False
        self.move_history = []
        self.win_pattern = None
        self.start_time = None
        self.move_times = []

    def get_board_state(self):
        """Return current board state"""
        return {
            'board': self.board,
            'current_player': self.current_player,
            'winner': self.winner,
            'game_over': self.game_over,
            'move_history': self.move_history,
            'win_pattern': self.win_pattern,
            'move_count': len(self.move_history)
        }

    def make_move(self, position):
        """
        Make a move at the specified position (0-8)
        Returns: (success, message, game_state)
        """
        # Comprehensive validation
        validation_error = self._validate_move(position)
        if validation_error:
            return False, validation_error, self.get_board_state()

        # Make the move
        self.board[position] = self.current_player
        self.move_history.append({
            'player': self.current_player,
            'position': position,
            'move_number': len(self.move_history) + 1,
            'timestamp': self._get_timestamp()
        })

        # Check for win or draw
        if self._check_win():
            self.winner = self.current_player
            self.game_over = True
            return True, f"🎉 Player {self.current_player} wins! 🎉", self.get_board_state()

        if self._check_draw():
            self.game_over = True
            return True, "🤝 Game is a draw! 🤝", self.get_board_state()

        # Switch player
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        return True, f"Player {self.current_player}'s turn", self.get_board_state()

    def _validate_move(self, position):
        """Validate if a move is legal"""
        if self.game_over:
            return "Game is already over. Please start a new game."

        if not isinstance(position, int):
            return "Invalid move: Position must be a number."

        if position < 0 or position > 8:
            return f"Invalid move: Position {position} is out of range (0-8)."

        if self.board[position] != '':
            return f"Invalid move: Position {position} is already taken by {self.board[position]}."

        return None

    def _check_win(self):
        """Check if current player has won"""
        win_patterns = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
            [0, 4, 8], [2, 4, 6]  # diagonals
        ]

        for pattern in win_patterns:
            if (self.board[pattern[0]] and
                    self.board[pattern[0]] == self.board[pattern[1]] == self.board[pattern[2]]):
                self.win_pattern = pattern
                return True
        return False

    def _check_draw(self):
        """Check if game is a draw"""
        return '' not in self.board and not self._check_win()

    def reset_game(self):
        """Reset the game to initial state"""
        self.board = [''] * 9
        self.current_player = 'X'
        self.winner = None
        self.game_over = False
        self.win_pattern = None
        # Keep move history for statistics but clear for new game
        self.move_history = []
        return self.get_board_state()

    def _get_timestamp(self):
        """Get current timestamp for move tracking"""
        from datetime import datetime
        return datetime.now().isoformat()

    def get_valid_moves(self):
        """Return list of available positions"""
        return [i for i, cell in enumerate(self.board) if cell == '']

    def get_winning_line(self):
        """Return the winning line if there is one"""
        return self.win_pattern

    def get_game_statistics(self):
        """Return game statistics"""
        return {
            'total_moves': len(self.move_history),
            'moves_by_player': {
                'X': len([m for m in self.move_history if m['player'] == 'X']),
                'O': len([m for m in self.move_history if m['player'] == 'O'])
            },
            'first_player': self.move_history[0]['player'] if self.move_history else None,
            'last_move': self.move_history[-1] if self.move_history else None
        }

    def is_valid_position(self, position):
        """Check if position is valid and empty"""
        return (isinstance(position, int) and
                0 <= position <= 8 and
                self.board[position] == '')