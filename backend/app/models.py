from datetime import datetime
from werkzeug.security import generate_password_hash
from .extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), default='user')
    is_super_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    league = db.Column(db.String(20), default='Iron')
    achievements = db.relationship('Achievement', backref='user', lazy=True, cascade='all, delete-orphan')
    discussions = db.relationship('Discussion', backref='author', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def calculate_league(self):
        leagues = ['Iron', 'Bronze', 'Silver', 'Gold', 'Diamond', 'Void', 'Joker']
        max_complexity = 0
        confirmed_achievements = [ach.difficulty for ach in self.achievements if ach.is_confirmed]
        if confirmed_achievements:
            max_complexity = max(confirmed_achievements)

        if max_complexity < 100:
            self.league = 'Iron'
        elif 100 <= max_complexity < 10000:
            self.league = 'Bronze'
        elif 10000 <= max_complexity < 1000000:
            self.league = 'Silver'
        elif 1000000 <= max_complexity < 100000000:
            self.league = 'Gold'
        elif 100000000 <= max_complexity < 10000000000:
            self.league = 'Diamond'
        elif 10000000000 <= max_complexity < 1000000000000:
            self.league = 'Void'
        else:
            self.league = 'Joker'

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bio = db.Column(db.Text)
    telegram = db.Column(db.String(50))
    discord = db.Column(db.String(50))
    avatar_url = db.Column(db.String(255))

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    difficulty = db.Column(db.BigInteger, nullable=False)
    link = db.Column(db.String(256)) # Link to proof
    is_confirmed = db.Column(db.Boolean, default=False) # Confirmed by administrator
    is_pending = db.Column(db.Boolean, default=True) # Awaiting confirmation
    rejected = db.Column(db.Boolean, default=False) # Rejected by administrator

    def __repr__(self):
        return f'<Achievement "{self.title}">'

class Discussion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='discussion', cascade='all, delete-orphan')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussion.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), cascade='all, delete-orphan')