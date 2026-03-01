from flask import Flask, render_template, session, request, jsonify
from game_logic import TicTacToe
import secrets
import os

app = Flask(__name__)
# Use environment variable in production, fallback for development
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Important: Configure session to be permanent and set cookie settings
app.config.update(
    SESSION_COOKIE_SECURE=False,  # Set to True only if using HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_PERMANENT=True,
    PERMANENT_SESSION_LIFETIME=3600  # 1 hour
)


@app.route('/')
def index():
    """Render the main game page"""
    # Initialize game in session if not exists
    if 'game' not in session:
        game = TicTacToe()
        session['game'] = game.get_board_state()
        session.permanent = True  # Make session permanent
    return render_template('index.html')


@app.route('/api/new-game', methods=['POST'])
def new_game():
    """Start a new game"""
    game = TicTacToe()
    session['game'] = game.get_board_state()
    session.permanent = True
    return jsonify({
        'success': True,
        'message': 'New game started',
        'game_state': session['game']
    })


@app.route('/api/move', methods=['POST'])
def make_move():
    """Process a player move"""
    # Check if game exists in session
    if 'game' not in session:
        # Initialize a new game if none exists
        game = TicTacToe()
        session['game'] = game.get_board_state()
        session.permanent = True
        return jsonify({
            'success': False,
            'message': 'No game in progress. Starting new game.',
            'game_state': session['game']
        })

    data = request.get_json()
    if not data or 'position' not in data:
        return jsonify({
            'success': False,
            'message': 'Invalid request: position required'
        }), 400

    position = data.get('position')

    # Validate position
    if not isinstance(position, int) or position < 0 or position > 8:
        return jsonify({
            'success': False,
            'message': 'Invalid position. Must be 0-8.'
        }), 400

    # Reconstruct game from session
    game = TicTacToe()
    try:
        game.board = session['game']['board']
        game.current_player = session['game']['current_player']
        game.winner = session['game']['winner']
        game.game_over = session['game']['game_over']
        game.move_history = session['game'].get('move_history', [])
    except (KeyError, TypeError) as e:
        # If session data is corrupted, start fresh
        game = TicTacToe()
        session['game'] = game.get_board_state()
        session.permanent = True
        return jsonify({
            'success': False,
            'message': 'Game state corrupted. Started new game.',
            'game_state': session['game']
        })

    # Make the move
    success, message, game_state = game.make_move(position)

    # Update session
    session['game'] = game_state
    session.permanent = True

    # Get winning line if game is won
    winning_line = None
    if game.winner:
        winning_line = game.get_winning_line()

    return jsonify({
        'success': success,
        'message': message,
        'game_state': game_state,
        'winning_line': winning_line
    })


@app.route('/api/game-state', methods=['GET'])
def get_game_state():
    """Get current game state"""
    if 'game' not in session:
        game = TicTacToe()
        session['game'] = game.get_board_state()
        session.permanent = True

    return jsonify({
        'success': True,
        'game_state': session['game']
    })


@app.route('/api/reset', methods=['POST'])
def reset_game():
    """Reset the current game"""
    game = TicTacToe()
    session['game'] = game.reset_game()
    session.permanent = True
    return jsonify({
        'success': True,
        'message': 'Game reset',
        'game_state': session['game']
    })


@app.route('/api/valid-moves', methods=['GET'])
def get_valid_moves():
    """Get list of valid moves"""
    game = TicTacToe()
    if 'game' in session:
        game.board = session['game']['board']
        game.game_over = session['game']['game_over']

    return jsonify({
        'valid_moves': game.get_valid_moves() if not game.game_over else []
    })


@app.route('/api/undo', methods=['POST'])
def undo_move():
    """Undo last move (for future use)"""
    if 'game' not in session:
        return jsonify({
            'success': False,
            'message': 'No game in progress'
        }), 400

    game = TicTacToe()
    game.board = session['game']['board']
    game.current_player = session['game']['current_player']
    game.winner = session['game']['winner']
    game.game_over = session['game']['game_over']
    game.move_history = session['game'].get('move_history', [])

    success, message, game_state = game.undo_move()
    session['game'] = game_state
    session.permanent = True

    return jsonify({
        'success': success,
        'message': message,
        'game_state': game_state
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'session_exists': 'game' in session,
        'session_data': session.get('game', {}).get('board') if 'game' in session else None
    }, 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)