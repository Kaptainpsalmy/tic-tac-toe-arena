from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import uuid

db = SQLAlchemy()


class User(db.Model):
    """Simple user model with UUID and nickname"""
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nickname = db.Column(db.String(50), nullable=False)

    # Statistics
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    draws = db.Column(db.Integer, default=0)
    elo = db.Column(db.Integer, default=1000)

    # Game tracking
    games_played = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)
    max_streak = db.Column(db.Integer, default=0)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    games_as_x = db.relationship('Game', foreign_keys='Game.player_x_id', backref='player_x', lazy='dynamic')
    games_as_o = db.relationship('Game', foreign_keys='Game.player_o_id', backref='player_o', lazy='dynamic')

    def update_last_seen(self):
        """Update last seen timestamp"""
        self.last_seen = datetime.utcnow()
        db.session.commit()

    def update_stats(self, won=None, moves_count=0, game_time=0):
        """Update statistics after a game"""
        self.games_played += 1

        if won is True:
            self.wins += 1
            self.current_streak += 1
            self.max_streak = max(self.max_streak, self.current_streak)
            self.elo += 10
        elif won is False:
            self.losses += 1
            self.current_streak = 0
            self.elo = max(1, self.elo - 5)
        else:  # draw
            self.draws += 1
            self.current_streak = 0

        self.last_seen = datetime.utcnow()
        db.session.commit()

    def get_win_rate(self):
        """Get win rate percentage"""
        if self.games_played == 0:
            return 0
        return round((self.wins / self.games_played) * 100, 1)

    def get_stats(self):
        """Get user statistics as dictionary"""
        return {
            'id': self.id,
            'nickname': self.nickname,
            'wins': self.wins,
            'losses': self.losses,
            'draws': self.draws,
            'elo': self.elo,
            'games_played': self.games_played,
            'current_streak': self.current_streak,
            'max_streak': self.max_streak,
            'win_rate': self.get_win_rate(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None
        }


class Game(db.Model):
    """Game history model"""
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String(50), unique=True, nullable=False)

    player_x_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    player_o_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)

    winner = db.Column(db.String(10))  # 'X', 'O', or 'draw'
    winning_line = db.Column(db.String(50))
    moves = db.Column(db.Text)
    move_count = db.Column(db.Integer, default=0)
    game_mode = db.Column(db.String(20), default='2p')

    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    duration = db.Column(db.Integer)

    def set_moves(self, moves_list):
        """Set moves from list"""
        self.moves = json.dumps(moves_list)
        self.move_count = len(moves_list)

    def get_moves(self):
        """Get moves as list"""
        return json.loads(self.moves) if self.moves else []

    def end_game(self, winner, winning_line=None):
        """End the game and record result"""
        self.winner = winner
        self.winning_line = json.dumps(winning_line) if winning_line else None
        self.ended_at = datetime.utcnow()
        self.duration = int((self.ended_at - self.started_at).total_seconds())
        db.session.commit()

    def to_dict(self):
        """Convert game to dictionary"""
        return {
            'game_id': self.game_id,
            'player_x': self.player_x.nickname if self.player_x else 'Guest',
            'player_o': self.player_o.nickname if self.player_o else 'Guest' + (
                ' (AI)' if self.game_mode != '2p' else ''),
            'winner': self.winner,
            'move_count': self.move_count,
            'game_mode': self.game_mode,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'duration': self.duration,
            'winning_line': json.loads(self.winning_line) if self.winning_line else None
        }


class GameInvite(db.Model):
    """Game invitation model"""
    __tablename__ = 'game_invites'

    id = db.Column(db.Integer, primary_key=True)
    invite_code = db.Column(db.String(20), unique=True, nullable=False)
    inviter_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    invitee_nickname = db.Column(db.String(50))
    game_mode = db.Column(db.String(20), default='2p')
    status = db.Column(db.String(20), default='pending')  # pending, accepted, declined, expired

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    accepted_at = db.Column(db.DateTime)

    def is_valid(self):
        """Check if invite is still valid"""
        return (self.status == 'pending' and
                datetime.utcnow() < self.expires_at)

    def accept(self):
        """Accept invitation"""
        self.status = 'accepted'
        self.accepted_at = datetime.utcnow()
        db.session.commit()


class Achievement(db.Model):
    """Achievement model"""
    __tablename__ = 'achievements'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    icon = db.Column(db.String(50))
    condition = db.Column(db.String(200))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon
        }


class UserAchievement(db.Model):
    """User achievements junction table"""
    __tablename__ = 'user_achievements'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'achievement_id', name='unique_user_achievement'),)