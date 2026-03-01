from flask import Flask, render_template, session, request, jsonify
from game_logic import TicTacToe
import secrets
import os
import logging
from datetime import timedelta
from ai_engine import TicTacToeAI, AIGameManager
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

ai_game_manager = AIGameManager()


# Session configuration
app.config.update(
    SESSION_COOKIE_SECURE=False,  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_PERMANENT=True,
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1)
)


@app.route('/')
def index():
    """Render the main game page"""
    try:
        if 'game' not in session:
            game = TicTacToe()
            session['game'] = game.get_board_state()
            session.permanent = True
            logger.debug("New game session created")
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        return render_template('error.html', error="Failed to load game"), 500


@app.route('/api/new-game', methods=['POST'])
def new_game():
    """Start a new game"""
    try:
        game = TicTacToe()
        session['game'] = game.get_board_state()
        session.permanent = True
        logger.debug("New game started")

        return jsonify({
            'success': True,
            'message': '🎮 New game started!',
            'game_state': session['game']
        })
    except Exception as e:
        logger.error(f"Error in new-game: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to start new game'
        }), 500


@app.route('/api/move', methods=['POST'])
def make_move():
    """Process a player move with comprehensive validation"""
    try:
        # Check if game exists
        if 'game' not in session:
            game = TicTacToe()
            session['game'] = game.get_board_state()
            session.permanent = True
            return jsonify({
                'success': False,
                'message': 'No game in progress. Starting new game.',
                'game_state': session['game']
            })

        # Validate request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Invalid request: No data provided'
            }), 400

        if 'position' not in data:
            return jsonify({
                'success': False,
                'message': 'Invalid request: Position required'
            }), 400

        position = data.get('position')

        # Validate position type
        if not isinstance(position, int):
            return jsonify({
                'success': False,
                'message': f'Invalid position type: Expected integer, got {type(position).__name__}'
            }), 400

        # Reconstruct game from session
        game = TicTacToe()
        try:
            game.board = session['game']['board']
            game.current_player = session['game']['current_player']
            game.winner = session['game']['winner']
            game.game_over = session['game']['game_over']
            game.move_history = session['game'].get('move_history', [])
            game.win_pattern = session['game'].get('win_pattern')
        except KeyError as e:
            logger.error(f"Session data corrupted: {str(e)}")
            game = TicTacToe()
            session['game'] = game.get_board_state()
            return jsonify({
                'success': False,
                'message': 'Game state corrupted. Started new game.',
                'game_state': session['game']
            })

        # Check if game is already over
        if game.game_over:
            return jsonify({
                'success': False,
                'message': 'Game is already over. Please start a new game.',
                'game_state': game.get_board_state()
            })

        # Make the move
        success, message, game_state = game.make_move(position)

        # Update session
        session['game'] = game_state

        # Prepare response
        response = {
            'success': success,
            'message': message,
            'game_state': game_state
        }

        # Add winning line if game is won
        if game.winner:
            response['winning_line'] = game.get_winning_line()
            response['statistics'] = game.get_game_statistics()

        return jsonify(response)

    except Exception as e:
        logger.error(f"Unexpected error in make_move: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred'
        }), 500


@app.route('/api/game-state', methods=['GET'])
def get_game_state():
    """Get current game state"""
    try:
        if 'game' not in session:
            game = TicTacToe()
            session['game'] = game.get_board_state()
            session.permanent = True

        return jsonify({
            'success': True,
            'game_state': session['game']
        })
    except Exception as e:
        logger.error(f"Error in game-state: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get game state'
        }), 500


@app.route('/api/reset', methods=['POST'])
def reset_game():
    """Reset the current game"""
    try:
        game = TicTacToe()
        session['game'] = game.reset_game()
        session.permanent = True

        return jsonify({
            'success': True,
            'message': 'Game reset successfully',
            'game_state': session['game']
        })
    except Exception as e:
        logger.error(f"Error in reset: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to reset game'
        }), 500


@app.route('/api/valid-moves', methods=['GET'])
def get_valid_moves():
    """Get list of valid moves"""
    try:
        game = TicTacToe()
        if 'game' in session:
            game.board = session['game']['board']
            game.game_over = session['game']['game_over']

        valid_moves = game.get_valid_moves() if not game.game_over else []

        return jsonify({
            'success': True,
            'valid_moves': valid_moves,
            'count': len(valid_moves)
        })
    except Exception as e:
        logger.error(f"Error in valid-moves: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get valid moves'
        }), 500


@app.route('/api/validate-position', methods=['POST'])
def validate_position():
    """Validate if a position is available"""
    try:
        data = request.get_json()
        position = data.get('position')

        if 'game' not in session:
            return jsonify({'valid': False, 'message': 'No game in progress'})

        game = TicTacToe()
        game.board = session['game']['board']

        valid = game.is_valid_position(position)

        return jsonify({
            'valid': valid,
            'message': 'Position is valid' if valid else 'Position is invalid or taken'
        })
    except Exception as e:
        logger.error(f"Error in validate-position: {str(e)}")
        return jsonify({'valid': False, 'message': 'Validation failed'}), 500


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get game statistics"""
    try:
        if 'game' not in session:
            return jsonify({'success': False, 'message': 'No game in progress'})

        game = TicTacToe()
        game.board = session['game']['board']
        game.move_history = session['game'].get('move_history', [])

        stats = game.get_game_statistics()

        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"Error in statistics: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to get statistics'}), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'session_exists': 'game' in session,
        'timestamp': __import__('datetime').datetime.now().isoformat()
    }, 200



@app.route('/api/ai-move', methods=['POST'])
def get_ai_move():
    """Get AI move for current board"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        difficulty = data.get('difficulty', 'medium')
        board = data.get('board')
        ai_player = data.get('ai_player', 'O')

        if not board or len(board) != 9:
            return jsonify({'success': False, 'message': 'Invalid board state'}), 400

        # Validate board data
        for cell in board:
            if cell not in ['', 'X', 'O']:
                return jsonify({'success': False, 'message': 'Invalid board data'}), 400

        # Create AI instance
        ai = TicTacToeAI(difficulty)

        # Get move
        move = ai.get_move(board, ai_player)

        if move == -1:
            return jsonify({
                'success': False,
                'message': 'No valid moves available'
            }), 400

        return jsonify({
            'success': True,
            'position': move,
            'thinking_time': ai.thinking_time,
            'difficulty': difficulty,
            'ai_name': ai.name,
            'personality': ai.get_personality()
        })

    except Exception as e:
        logger.error(f"Error in ai-move: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'AI failed to compute move'
        }), 500


@app.route('/api/ai-personality', methods=['POST'])
def get_ai_personality():
    """Get AI personality based on difficulty"""
    try:
        data = request.get_json()
        difficulty = data.get('difficulty', 'medium')

        ai = TicTacToeAI(difficulty)
        personality = ai.get_personality()

        return jsonify({
            'success': True,
            'personality': personality
        })
    except Exception as e:
        logger.error(f"Error in ai-personality: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to get personality'}), 500


@app.route('/api/ai-stats', methods=['GET', 'POST'])
def handle_ai_stats():
    """Get or update AI statistics"""
    global ai_game_manager

    if request.method == 'GET':
        return jsonify({
            'success': True,
            'stats': ai_game_manager.get_stats()
        })

    elif request.method == 'POST':
        try:
            data = request.get_json()
            winner = data.get('winner')
            ai_player = data.get('ai_player', 'O')

            ai_game_manager.update_stats(winner, ai_player)

            return jsonify({
                'success': True,
                'stats': ai_game_manager.get_stats()
            })
        except Exception as e:
            logger.error(f"Error updating stats: {str(e)}")
            return jsonify({'success': False, 'message': 'Failed to update stats'}), 500


@app.route('/api/ai-reset-stats', methods=['POST'])
def reset_ai_stats():
    """Reset AI statistics"""
    global ai_game_manager
    ai_game_manager.reset_stats()
    return jsonify({
        'success': True,
        'message': 'Statistics reset successfully'
    })


@app.route('/api/ai-validate-move', methods=['POST'])
def validate_ai_move():
    """Validate if a move would be good (for hints)"""
    try:
        data = request.get_json()
        position = data.get('position')
        difficulty = data.get('difficulty', 'medium')
        board = data.get('board')
        player = data.get('player', 'X')

        ai = TicTacToeAI(difficulty)
        ai_move = ai.get_move(board, 'O' if player == 'X' else 'X')

        # Simple validation - is this what AI would play?
        is_optimal = (position == ai_move)

        return jsonify({
            'success': True,
            'is_optimal': is_optimal,
            'ai_would_play': ai_move,
            'message': 'Good move!' if is_optimal else 'AI would play differently'
        })
    except Exception as e:
        logger.error(f"Error validating move: {str(e)}")
        return jsonify({'success': False, 'message': 'Validation failed'}), 500


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Resource not found'}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'success': False, 'message': 'Method not allowed'}), 405


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)