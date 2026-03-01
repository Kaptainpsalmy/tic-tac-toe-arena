class TicTacToe:
    def __init__(self):
        self.board = [''] * 9
        self.current_player = 'X'
        self.winner = None
        self.game_over = False
        self.move_history = []

    def get_board_state(self):
        """Return current board state"""
        return {
            'board': self.board,
            'current_player': self.current_player,
            'winner': self.winner,
            'game_over': self.game_over,
            'move_history': self.move_history
        }

    def make_move(self, position):
        """
        Make a move at the specified position (0-8)
        Returns: (success, message, game_state)
        """
        # Validate move
        if self.game_over:
            return False, "Game is already over", self.get_board_state()

        if position < 0 or position > 8:
            return False, "Invalid position", self.get_board_state()

        if self.board[position] != '':
            return False, "Position already taken", self.get_board_state()

        # Make the move
        self.board[position] = self.current_player
        self.move_history.append({
            'player': self.current_player,
            'position': position,
            'move_number': len(self.move_history) + 1
        })

        # Check for win or draw
        if self.check_win():
            self.winner = self.current_player
            self.game_over = True
            return True, f"Player {self.current_player} wins!", self.get_board_state()

        if self.check_draw():
            self.game_over = True
            return True, "Game is a draw!", self.get_board_state()

        # Switch player
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        return True, f"Player {self.current_player}'s turn", self.get_board_state()

    def check_win(self):
        """Check if current player has won"""
        win_patterns = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
            [0, 4, 8], [2, 4, 6]  # diagonals
        ]

        for pattern in win_patterns:
            if (self.board[pattern[0]] and
                    self.board[pattern[0]] == self.board[pattern[1]] == self.board[pattern[2]]):
                return True
        return False

    def check_draw(self):
        """Check if game is a draw"""
        return '' not in self.board and not self.check_win()

    def reset_game(self):
        """Reset the game to initial state"""
        self.board = [''] * 9
        self.current_player = 'X'
        self.winner = None
        self.game_over = False
        self.move_history = []
        return self.get_board_state()

    def get_valid_moves(self):
        """Return list of available positions"""
        return [i for i, cell in enumerate(self.board) if cell == '']

    def get_winning_line(self):
        """Return the winning line if there is one"""
        win_patterns = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]

        for pattern in win_patterns:
            if (self.board[pattern[0]] and
                    self.board[pattern[0]] == self.board[pattern[1]] == self.board[pattern[2]]):
                return pattern
        return None
    def undo_move(self):
        """Undo last move (useful for future AI features)"""
        if not self.move_history:
            return False, "No moves to undo", self.get_board_state()

        last_move = self.move_history.pop()
        self.board[last_move['position']] = ''
        self.current_player = last_move['player']
        self.winner = None
        self.game_over = False
        return True, "Move undone", self.get_board_state()