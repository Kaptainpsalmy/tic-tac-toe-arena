#!/usr/bin/env python3
"""Database migration script for Tic Tac Toe Arena"""

import os
import sys
from datetime import datetime
from app import app
from models import db, User, UserStats, Game, Achievement, GameInvite


def init_db():
    """Initialize database"""
    with app.app_context():
        print("📦 Creating database tables...")
        db.create_all()
        print("✅ Database tables created successfully!")


def create_achievements():
    """Create default achievements"""
    with app.app_context():
        print("🏆 Creating default achievements...")

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
                'name': 'Perfect Game',
                'description': 'Win without opponent making a move',
                'icon': '⭐',
                'condition': '{"perfect": true}'
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
            },
            {
                'name': 'Comeback King',
                'description': 'Win from a losing position',
                'icon': '👑',
                'condition': '{"comeback": true}'
            }
        ]

        for ach in achievements:
            existing = Achievement.query.filter_by(name=ach['name']).first()
            if not existing:
                new_ach = Achievement(**ach)
                db.session.add(new_ach)

        db.session.commit()
        print("✅ Achievements created successfully!")


def reset_db():
    """Reset database (drop all tables)"""
    with app.app_context():
        print("⚠️  Dropping all tables...")
        db.drop_all()
        print("✅ Tables dropped successfully!")


def seed_db():
    """Seed database with test data"""
    with app.app_context():
        print("🌱 Seeding database with test data...")

        # Create test user
        test_user = User(
            username='testuser',
            email='test@example.com'
        )
        test_user.set_password('password123')
        db.session.add(test_user)
        db.session.flush()

        # Create stats for test user
        stats = UserStats(
            user_id=test_user.id,
            games_played=10,
            wins=5,
            losses=3,
            draws=2,
            elo_rating=1250,
            current_win_streak=2,
            max_win_streak=3
        )
        db.session.add(stats)
        db.session.commit()

        print("✅ Test data created successfully!")
        print(f"   Username: testuser")
        print(f"   Password: password123")


def backup_db():
    """Backup database"""
    import shutil
    from datetime import datetime

    if os.path.exists('tic_tac_toe.db'):
        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2('tic_tac_toe.db', backup_name)
        print(f"✅ Database backed up to {backup_name}")
    else:
        print("❌ Database file not found!")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Database management for Tic Tac Toe Arena')
    parser.add_argument('command', choices=['init', 'reset', 'seed', 'achievements', 'backup'],
                        help='Command to execute')

    args = parser.parse_args()

    if args.command == 'init':
        init_db()
        create_achievements()
    elif args.command == 'reset':
        reset_db()
    elif args.command == 'seed':
        seed_db()
    elif args.command == 'achievements':
        create_achievements()
    elif args.command == 'backup':
        backup_db()