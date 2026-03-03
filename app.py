from flask import Flask, render_template, session, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import secrets
import os
import json
import logging
import uuid

# Game logic imports
from game_logic import TicTacToe
from ai_engine import TicTacToeAI, AIGameManager

# Import models
from models import db, User, Game, GameInvite, Achievement, UserAchievement

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///tic_tac_toe.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Session configuration
app.config.update(
    SESSION_COOKIE_SECURE=False,  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_PERMANENT=True,
    PERMANENT_SESSION_LIFETIME=timedelta(days=365)  # Long-lived sessions
)

# Initialize extensions
db.init_app(app)

# AI Game Manager
ai_game_manager = AIGameManager()


def create_default_achievements():
    """Create default achievements"""
    achievements = [
        {
            'name': 'First Victory',
            'description': 'Win your first game',
            'icon': '🏆',
            'condition': '{"wins": 1}'
        },
        {
            'name': 'Win Streak',
            'description': 'Win 3 games in a row',
            'icon': '🔥',
            'condition': '{"streak": 3}'
        },
        {
            'name': 'Grandmaster',
            'description': 'Reach 1500 ELO rating',
            'icon': '👑',
            'condition': '{"elo": 1500}'
        },
        {
            'name': 'Veteran',
            'description': 'Play 100 games',
            'icon': '🎮',
            'condition': '{"games": 100}'
        },
        {
            'name': 'AI Slayer',
            'description': 'Beat the Expert AI',
            'icon': '🤖',
            'condition': '{"beat_ai": true}'
        }
    ]

    for ach in achievements:
        existing = Achievement.query.filter_by(name=ach['name']).first()
        if not existing:
            new_ach = Achievement(
                name=ach['name'],
                description=ach['description'],
                icon=ach['icon'],
                condition=ach['condition']
            )
            db.session.add(new_ach)

    db.session.commit()


# Create tables
with app.app_context():
    db.create_all()
    create_default_achievements()


# ============ MAIN ROUTES ============

@app.route('/')
def index():
    """Render the main game page"""
    try:
        if 'game' not in session:
            game = TicTacToe()
            session['game'] = game.get_board_state()
            session.permanent = True
            logger.debug("New game session created")

        # Get user info for template
        user = None
        if 'user_id' in session:
            user = User.query.get(session['user_id'])

        return render_template('index.html', current_user=user)
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        return render_template('error.html', error="Failed to load game"), 500


# ============ SIMPLE NICKNAME LOGIN ============

@app.route('/enter-arena')
def enter_arena_page():
    """Show simple login page"""
    return render_template('simple_login.html')


@app.route('/api/enter-arena', methods=['POST'])
def enter_arena():
    """Simple nickname login"""
    try:
        data = request.get_json()
        nickname = data.get('nickname', '').strip()

        if not nickname:
            return jsonify({'success': False, 'message': 'Nickname required'}), 400

        if len(nickname) > 30:
            return jsonify({'success': False, 'message': 'Nickname too long (max 30 chars)'}), 400

        # Check if user exists by nickname (optional - allow multiple users with same nickname)
        user = User.query.filter_by(nickname=nickname).first()

        if not user:
            # Create new user with UUID
            user = User(
                nickname=nickname
            )
            db.session.add(user)
            db.session.commit()
            logger.info(f"New user created: {nickname} with ID {user.id}")

        # Store in session
        session['user_id'] = user.id
        session['nickname'] = user.nickname
        session.permanent = True

        # Update last seen
        user.update_last_seen()

        return jsonify({
            'success': True,
            'user': user.get_stats()
        })

    except Exception as e:
        logger.error(f"Error in enter_arena: {str(e)}")
        return jsonify({'success': False, 'message': 'Login failed'}), 500


@app.route('/logout')
def logout():
    """Simple logout"""
    session.clear()
    return redirect(url_for('enter_arena_page'))


# ============ USER PROFILE ROUTES ============

@app.route('/api/user/profile')
def get_profile():
    """Get user profile"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    return jsonify({
        'success': True,
        'user': user.get_stats()
    })


@app.route('/api/user/stats')
def get_user_stats():
    """Get user statistics"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    recent_games = Game.query.filter(
        (Game.player_x_id == user.id) | (Game.player_o_id == user.id)
    ).order_by(Game.started_at.desc()).limit(10).all()

    return jsonify({
        'success': True,
        'stats': user.get_stats(),
        'recent_games': [game.to_dict() for game in recent_games]
    })


@app.route('/api/user/achievements')
def get_achievements():
    """Get user's achievements"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    user_achievements = UserAchievement.query.filter_by(user_id=user.id).all()
    earned_ids = [ua.achievement_id for ua in user_achievements]

    all_achievements = Achievement.query.all()

    result = []
    for ach in all_achievements:
        result.append({
            **ach.to_dict(),
            'earned': ach.id in earned_ids,
            'earned_at': next(
                (ua.earned_at.isoformat() for ua in user_achievements if ua.achievement_id == ach.id),
                None
            )
        })

    return jsonify({
        'success': True,
        'achievements': result
    })


# ============ GAME ROUTES WITH DATABASE ============

@app.route('/api/save-game', methods=['POST'])
def save_game():
    """Save completed game to database"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    try:
        data = request.get_json()
        user = User.query.get(session['user_id'])

        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        # Generate unique game ID
        game_id = secrets.token_urlsafe(8)

        # Determine player IDs
        player_x_id = user.id if data.get('player_x') == user.nickname else None
        player_o_id = user.id if data.get('player_o') == user.nickname else None

        # Create game record
        game = Game(
            game_id=game_id,
            player_x_id=player_x_id,
            player_o_id=player_o_id,
            winner=data.get('winner'),
            game_mode=data.get('game_mode', '2p'),
            started_at=datetime.fromisoformat(data.get('started_at')) if data.get('started_at') else datetime.utcnow(),
            ended_at=datetime.utcnow()
        )

        if data.get('winning_line'):
            game.winning_line = json.dumps(data.get('winning_line'))

        game.set_moves(data.get('moves', []))

        # Calculate duration
        if data.get('started_at'):
            start = datetime.fromisoformat(data['started_at'])
            game.duration = int((datetime.utcnow() - start).total_seconds())

        db.session.add(game)
        db.session.commit()

        # Update player statistics
        if player_x_id:
            update_player_stats(player_x_id, game)
        if player_o_id and player_o_id != player_x_id:
            update_player_stats(player_o_id, game)

        return jsonify({
            'success': True,
            'message': 'Game saved successfully',
            'game_id': game_id
        })

    except Exception as e:
        logger.error(f"Error saving game: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to save game'}), 500


def update_player_stats(user_id, game):
    """Update player statistics after game"""
    user = User.query.get(user_id)
    if not user:
        return

    # Determine if player won
    if game.winner == 'draw':
        user.update_stats(won=None, moves_count=game.move_count, game_time=game.duration or 0)
    else:
        player_symbol = 'X' if user_id == game.player_x_id else 'O'
        won = (game.winner == player_symbol)
        user.update_stats(won=won, moves_count=game.move_count, game_time=game.duration or 0)

    # Check achievements
    check_achievements(user)


def check_achievements(user):
    """Check and award achievements"""
    achievements_to_award = []

    # Check each achievement
    for achievement in Achievement.query.all():
        # Check if already earned
        if UserAchievement.query.filter_by(
                user_id=user.id,
                achievement_id=achievement.id
        ).first():
            continue

        condition = json.loads(achievement.condition)

        # Check conditions
        earned = False
        if 'wins' in condition and user.wins >= condition['wins']:
            earned = True
        elif 'streak' in condition and user.max_streak >= condition['streak']:
            earned = True
        elif 'elo' in condition and user.elo >= condition['elo']:
            earned = True
        elif 'games' in condition and user.games_played >= condition['games']:
            earned = True

        if earned:
            user_ach = UserAchievement(
                user_id=user.id,
                achievement_id=achievement.id
            )
            db.session.add(user_ach)
            achievements_to_award.append(achievement)

    if achievements_to_award:
        db.session.commit()

    return achievements_to_award


@app.route('/api/games/history')
def get_game_history():
    """Get user's game history"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        games = Game.query.filter(
            (Game.player_x_id == session['user_id']) | (Game.player_o_id == session['user_id'])
        ).order_by(Game.started_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'success': True,
            'games': [game.to_dict() for game in games.items],
            'total': games.total,
            'pages': games.pages,
            'current_page': games.page
        })
    except Exception as e:
        logger.error(f"Error in game history: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to get game history'}), 500


@app.route('/api/games/<game_id>')
def get_game(game_id):
    """Get specific game details"""
    try:
        game = Game.query.filter_by(game_id=game_id).first()
        if not game:
            return jsonify({'success': False, 'message': 'Game not found'}), 404

        return jsonify({
            'success': True,
            'game': game.to_dict(),
            'moves': game.get_moves()
        })
    except Exception as e:
        logger.error(f"Error getting game: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to get game'}), 500


# ============ LEADERBOARD ============

@app.route('/api/leaderboard')
def get_leaderboard():
    """Get global leaderboard"""
    try:
        timeframe = request.args.get('timeframe', 'all')
        limit = request.args.get('limit', 50, type=int)

        query = User.query.order_by(User.elo.desc())

        # Apply timeframe filter
        if timeframe == 'daily':
            cutoff = datetime.utcnow() - timedelta(days=1)
            query = query.filter(User.last_seen >= cutoff)
        elif timeframe == 'weekly':
            cutoff = datetime.utcnow() - timedelta(days=7)
            query = query.filter(User.last_seen >= cutoff)
        elif timeframe == 'monthly':
            cutoff = datetime.utcnow() - timedelta(days=30)
            query = query.filter(User.last_seen >= cutoff)

        leaderboard = query.limit(limit).all()

        return jsonify({
            'success': True,
            'leaderboard': [{
                'rank': i + 1,
                'nickname': user.nickname,
                'elo': user.elo,
                'wins': user.wins,
                'losses': user.losses,
                'draws': user.draws,
                'games': user.games_played,
                'win_rate': user.get_win_rate()
            } for i, user in enumerate(leaderboard)]
        })
    except Exception as e:
        logger.error(f"Error in leaderboard: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to get leaderboard'}), 500


# ============ INVITE SYSTEM ============

@app.route('/api/invite/create', methods=['POST'])
def create_invite():
    """Create game invitation"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    try:
        data = request.get_json()
        invitee_nickname = data.get('nickname')
        game_mode = data.get('game_mode', '2p')

        # Generate invite code
        invite_code = secrets.token_urlsafe(8)

        invite = GameInvite(
            invite_code=invite_code,
            inviter_id=session['user_id'],
            invitee_nickname=invitee_nickname,
            game_mode=game_mode,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )

        db.session.add(invite)
        db.session.commit()

        return jsonify({
            'success': True,
            'invite_code': invite_code,
            'invite_link': url_for('accept_invite', code=invite_code, _external=True)
        })
    except Exception as e:
        logger.error(f"Error creating invite: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to create invite'}), 500


@app.route('/invite/<code>')
def accept_invite(code):
    """Accept game invitation"""
    try:
        invite = GameInvite.query.filter_by(invite_code=code).first()

        if not invite or not invite.is_valid():
            return render_template('invite_expired.html'), 404

        if 'user_id' in session:
            # User is logged in, accept invite
            invite.accept()
            session['active_invite'] = code
            return redirect(url_for('index'))
        else:
            # User needs to login
            return redirect(url_for('enter_arena_page', next=f'/invite/{code}'))
    except Exception as e:
        logger.error(f"Error accepting invite: {str(e)}")
        return render_template('error.html', error="Failed to accept invite"), 500


# ============ GAME ROUTES ============

@app.route('/api/new-game', methods=['POST'])
def new_game():
    """Start a new game"""
    try:
        game = TicTacToe()
        session['game'] = game.get_board_state()
        session['game_started'] = datetime.utcnow().isoformat()
        session.permanent = True
        logger.debug("New game started")

        return jsonify({
            'success': True,
            'message': '🎮 New game started!',
            'game_state': session['game'],
            'started_at': session['game_started']
        })
    except Exception as e:
        logger.error(f"Error in new-game: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to start new game'
        }), 500


@app.route('/api/move', methods=['POST'])
def make_move():
    """Process a player move"""
    try:
        if 'game' not in session:
            game = TicTacToe()
            session['game'] = game.get_board_state()
            session['game_started'] = datetime.utcnow().isoformat()
            session.permanent = True
            return jsonify({
                'success': False,
                'message': 'No game in progress. Starting new game.',
                'game_state': session['game']
            })

        data = request.get_json()
        if not data or 'position' not in data:
            return jsonify({'success': False, 'message': 'Invalid request'}), 400

        position = data.get('position')
        if not isinstance(position, int) or position < 0 or position > 8:
            return jsonify({'success': False, 'message': 'Invalid position'}), 400

        # Reconstruct game from session
        game = TicTacToe()
        try:
            game.board = session['game']['board']
            game.current_player = session['game']['current_player']
            game.winner = session['game']['winner']
            game.game_over = session['game']['game_over']
            game.move_history = session['game'].get('move_history', [])
            game.win_pattern = session['game'].get('win_pattern')
        except KeyError:
            game = TicTacToe()
            session['game'] = game.get_board_state()
            session['game_started'] = datetime.utcnow().isoformat()
            return jsonify({
                'success': False,
                'message': 'Game state corrupted. Started new game.',
                'game_state': session['game']
            })

        if game.game_over:
            return jsonify({
                'success': False,
                'message': 'Game is already over. Please start a new game.',
                'game_state': game.get_board_state()
            })

        success, message, game_state = game.make_move(position)
        session['game'] = game_state

        response = {
            'success': success,
            'message': message,
            'game_state': game_state
        }

        if game.winner:
            response['winning_line'] = game.get_winning_line()
            response['statistics'] = game.get_game_statistics()

            # Auto-save game if user is logged in
            if 'user_id' in session and game.game_over:
                save_game_automatically(game)

        return jsonify(response)

    except Exception as e:
        logger.error(f"Unexpected error in make_move: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred'}), 500


def save_game_automatically(game):
    """Automatically save completed game for logged-in users"""
    try:
        if 'user_id' not in session:
            return

        game_id = secrets.token_urlsafe(8)
        user = User.query.get(session['user_id'])

        if not user:
            return

        db_game = Game(
            game_id=game_id,
            player_x_id=user.id if game.current_player == 'X' else None,
            player_o_id=user.id if game.current_player == 'O' else None,
            winner=game.winner,
            winning_line=json.dumps(game.win_pattern) if game.win_pattern else None,
            game_mode=session.get('game_mode', '2p'),
            started_at=datetime.fromisoformat(session.get('game_started', datetime.utcnow().isoformat())),
            ended_at=datetime.utcnow()
        )

        db_game.set_moves([{
            'player': move['player'],
            'position': move['position'],
            'move_number': move['move_number']
        } for move in game.move_history])

        if session.get('game_started'):
            start = datetime.fromisoformat(session['game_started'])
            db_game.duration = int((datetime.utcnow() - start).total_seconds())

        db.session.add(db_game)
        db.session.commit()

        # Update player stats
        update_player_stats(user.id, db_game)

    except Exception as e:
        logger.error(f"Error auto-saving game: {str(e)}")


# ============ EXISTING GAME ROUTES ============

@app.route('/api/game-state', methods=['GET'])
def get_game_state():
    """Get current game state"""
    try:
        if 'game' not in session:
            game = TicTacToe()
            session['game'] = game.get_board_state()
            session['game_started'] = datetime.utcnow().isoformat()
            session.permanent = True

        return jsonify({
            'success': True,
            'game_state': session['game']
        })
    except Exception as e:
        logger.error(f"Error in game-state: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to get game state'}), 500


@app.route('/api/reset', methods=['POST'])
def reset_game():
    """Reset the current game"""
    try:
        game = TicTacToe()
        session['game'] = game.reset_game()
        session['game_started'] = datetime.utcnow().isoformat()
        session.permanent = True

        return jsonify({
            'success': True,
            'message': 'Game reset successfully',
            'game_state': session['game']
        })
    except Exception as e:
        logger.error(f"Error in reset: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to reset game'}), 500


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
        return jsonify({'success': False, 'message': 'Failed to get valid moves'}), 500


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


@app.route('/api/undo', methods=['POST'])
def undo_move():
    """Undo last move"""
    try:
        if 'game' not in session:
            return jsonify({'success': False, 'message': 'No game in progress'}), 400

        game = TicTacToe()
        game.board = session['game']['board']
        game.current_player = session['game']['current_player']
        game.winner = session['game']['winner']
        game.game_over = session['game']['game_over']
        game.move_history = session['game'].get('move_history', [])

        success, message, game_state = game.undo_move()
        session['game'] = game_state

        return jsonify({
            'success': success,
            'message': message,
            'game_state': game_state
        })
    except Exception as e:
        logger.error(f"Error in undo: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to undo move'}), 500


# ============ AI ROUTES ============

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

        for cell in board:
            if cell not in ['', 'X', 'O']:
                return jsonify({'success': False, 'message': 'Invalid board data'}), 400

        ai = TicTacToeAI(difficulty)
        move = ai.get_move(board, ai_player)

        if move == -1:
            return jsonify({'success': False, 'message': 'No valid moves available'}), 400

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
        return jsonify({'success': False, 'message': 'AI failed to compute move'}), 500


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


# ============ HEALTH CHECK ============

@app.route('/health')
def health():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'session_exists': 'game' in session,
        'database': 'connected',
        'timestamp': datetime.now().isoformat()
    }, 200


# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'message': 'Resource not found'}), 404
    return render_template('error.html', error="Page not found"), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'success': False, 'message': 'Method not allowed'}), 405


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'success': False, 'message': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)