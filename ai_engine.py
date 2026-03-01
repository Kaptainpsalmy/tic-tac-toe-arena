import random
import math
from typing import List, Tuple, Optional


class TicTacToeAI:
    """Base AI class with multiple difficulty levels"""

    def __init__(self, difficulty='medium'):
        self.difficulty = difficulty
        self.thinking_time = self._get_thinking_time()
        self.name = self._get_ai_name()

    def _get_ai_name(self):
        """Get AI name based on difficulty"""
        names = {
            'easy': 'Novice AI',
            'medium': 'Tactical AI',
            'hard': 'Master AI',
            'expert': 'Grandmaster AI'
        }
        return names.get(self.difficulty, 'AI Opponent')

    def _get_thinking_time(self):
        """Get thinking time based on difficulty"""
        times = {
            'easy': 0.3,
            'medium': 0.6,
            'hard': 1.0,
            'expert': 1.5
        }
        return times.get(self.difficulty, 0.5)

    def get_move(self, board: List[str], ai_player: str = 'O') -> int:
        """
        Get AI move based on difficulty level
        """
        available_moves = [i for i, cell in enumerate(board) if cell == '']

        if not available_moves:
            return -1

        if self.difficulty == 'easy':
            return self._easy_ai(available_moves)
        elif self.difficulty == 'medium':
            return self._medium_ai(board, available_moves, ai_player)
        elif self.difficulty == 'hard':
            return self._hard_ai(board, ai_player)
        elif self.difficulty == 'expert':
            return self._expert_ai(board, ai_player)
        else:
            return self._medium_ai(board, available_moves, ai_player)

    def _easy_ai(self, available_moves: List[int]) -> int:
        """Easy AI: Random moves"""
        return random.choice(available_moves)

    def _medium_ai(self, board: List[str], available_moves: List[int], ai_player: str) -> int:
        """
        Medium AI:
        - Takes winning moves
        - Blocks opponent wins
        - Prefers center and corners
        """
        opponent = 'X' if ai_player == 'O' else 'O'

        # Check if AI can win
        for move in available_moves:
            if self._would_win(board, move, ai_player):
                return move

        # Check if need to block opponent win
        for move in available_moves:
            if self._would_win(board, move, opponent):
                return move

        # Prefer center
        if 4 in available_moves:
            return 4

        # Prefer corners
        corners = [0, 2, 6, 8]
        random.shuffle(corners)
        for corner in corners:
            if corner in available_moves:
                return corner

        # Otherwise random
        return random.choice(available_moves)

    def _hard_ai(self, board: List[str], ai_player: str) -> int:
        """Hard AI: Minimax algorithm"""
        opponent = 'X' if ai_player == 'O' else 'O'
        _, best_move = self._minimax(board, ai_player, ai_player, opponent, depth=0)
        return best_move

    def _expert_ai(self, board: List[str], ai_player: str) -> int:
        """Expert AI: Minimax with alpha-beta pruning (unbeatable)"""
        opponent = 'X' if ai_player == 'O' else 'O'
        _, best_move = self._minimax_alpha_beta(
            board, ai_player, ai_player, opponent,
            alpha=-math.inf, beta=math.inf, depth=0
        )
        return best_move if best_move != -1 else self._easy_ai(self._get_available_moves(board))

    def _minimax(self, board: List[str], current_player: str,
                 ai_player: str, opponent: str, depth: int) -> Tuple[int, int]:
        """
        Minimax algorithm for perfect play
        """
        # Check terminal states
        winner = self._check_winner(board)
        if winner == ai_player:
            return (10 - depth, -1)
        elif winner == opponent:
            return (depth - 10, -1)
        elif self._is_draw(board):
            return (0, -1)

        available_moves = self._get_available_moves(board)

        if current_player == ai_player:
            # Maximizing player
            best_score = -math.inf
            best_move = available_moves[0] if available_moves else -1

            for move in available_moves:
                board[move] = ai_player
                score, _ = self._minimax(board, opponent, ai_player, opponent, depth + 1)
                board[move] = ''

                if score > best_score:
                    best_score = score
                    best_move = move

            return (best_score, best_move)
        else:
            # Minimizing player
            best_score = math.inf
            best_move = available_moves[0] if available_moves else -1

            for move in available_moves:
                board[move] = opponent
                score, _ = self._minimax(board, ai_player, ai_player, opponent, depth + 1)
                board[move] = ''

                if score < best_score:
                    best_score = score
                    best_move = move

            return (best_score, best_move)

    def _minimax_alpha_beta(self, board: List[str], current_player: str,
                            ai_player: str, opponent: str,
                            alpha: float, beta: float, depth: int) -> Tuple[int, int]:
        """
        Minimax with alpha-beta pruning for faster, unbeatable AI
        """
        # Check terminal states
        winner = self._check_winner(board)
        if winner == ai_player:
            return (10 - depth, -1)
        elif winner == opponent:
            return (depth - 10, -1)
        elif self._is_draw(board):
            return (0, -1)

        available_moves = self._get_available_moves(board)

        if current_player == ai_player:
            # Maximizing player
            best_score = -math.inf
            best_move = available_moves[0] if available_moves else -1

            for move in available_moves:
                board[move] = ai_player
                score, _ = self._minimax_alpha_beta(
                    board, opponent, ai_player, opponent,
                    alpha, beta, depth + 1
                )
                board[move] = ''

                if score > best_score:
                    best_score = score
                    best_move = move

                # Alpha-beta pruning
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break

            return (best_score, best_move)
        else:
            # Minimizing player
            best_score = math.inf
            best_move = available_moves[0] if available_moves else -1

            for move in available_moves:
                board[move] = opponent
                score, _ = self._minimax_alpha_beta(
                    board, ai_player, ai_player, opponent,
                    alpha, beta, depth + 1
                )
                board[move] = ''

                if score < best_score:
                    best_score = score
                    best_move = move

                # Alpha-beta pruning
                beta = min(beta, best_score)
                if beta <= alpha:
                    break

            return (best_score, best_move)

    def _would_win(self, board: List[str], move: int, player: str) -> bool:
        """Check if making this move would win the game"""
        board[move] = player
        win = self._check_winner(board) == player
        board[move] = ''
        return win

    def _check_winner(self, board: List[str]) -> Optional[str]:
        """Check if there's a winner"""
        win_patterns = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
            [0, 4, 8], [2, 4, 6]  # diagonals
        ]

        for pattern in win_patterns:
            if (board[pattern[0]] and
                    board[pattern[0]] == board[pattern[1]] == board[pattern[2]]):
                return board[pattern[0]]
        return None

    def _is_draw(self, board: List[str]) -> bool:
        """Check if game is a draw"""
        return '' not in board and self._check_winner(board) is None

    def _get_available_moves(self, board: List[str]) -> List[int]:
        """Get list of available moves"""
        return [i for i, cell in enumerate(board) if cell == '']

    def get_personality(self) -> dict:
        """Get AI personality for UI"""
        personalities = {
            'easy': {
                'name': '🤖 Novice AI',
                'color': '#22c55e',
                'description': 'Makes random moves - Perfect for beginners!'
            },
            'medium': {
                'name': '🎯 Tactical AI',
                'color': '#f59e0b',
                'description': 'Blocks your wins and takes center - Getting tricky!'
            },
            'hard': {
                'name': '🧠 Master AI',
                'color': '#ef4444',
                'description': 'Uses minimax strategy - Quite challenging!'
            },
            'expert': {
                'name': '👑 Grandmaster AI',
                'color': '#8b5cf6',
                'description': 'Unbeatable - Can you force a draw?'
            }
        }
        return personalities.get(self.difficulty, personalities['medium'])


class AIGameManager:
    """Manages AI game sessions and statistics"""

    def __init__(self):
        self.games_played = 0
        self.ai_wins = 0
        player_wins = 0
        self.draws = 0
        self.current_streak = 0

    def update_stats(self, winner: Optional[str], ai_player: str = 'O'):
        """Update game statistics"""
        self.games_played += 1

        if winner == ai_player:
            self.ai_wins += 1
            self.current_streak += 1
        elif winner is None:
            self.draws += 1
            self.current_streak = 0
        else:
            self.player_wins += 1
            self.current_streak = 0

    def get_stats(self) -> dict:
        """Get current statistics"""
        return {
            'games_played': self.games_played,
            'ai_wins': self.ai_wins,
            'player_wins': self.player_wins,
            'draws': self.draws,
            'win_rate': round((self.ai_wins / max(self.games_played, 1)) * 100, 1),
            'current_streak': self.current_streak
        }

    def reset_stats(self):
        """Reset all statistics"""
        self.games_played = 0
        self.ai_wins = 0
        self.player_wins = 0
        self.draws = 0
        self.current_streak = 0