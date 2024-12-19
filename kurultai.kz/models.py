from datetime import datetime
from extensions import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    gender = db.Column(db.String(10))
    phone_number = db.Column(db.String(15))
    group_num = db.Column(db.String(50))
    date_of_birth = db.Column(db.Date)
    last_active = db.Column(db.DateTime)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_active = db.Column(db.Boolean, default=True)

    # Flask-Login использует этот метод для получения идентификатора пользователя
    def get_id(self):
        return str(self.user_id)


class UsersRank(db.Model):
    __tablename__ = 'users_rank'
    rank_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'))
    rank_name = db.Column(db.String(50), nullable=False)
    points = db.Column(db.Integer, default=0)

class Tournament(db.Model):
    __tablename__ = 'tournaments'
    tournament_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    winner_team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id', ondelete='SET NULL'), nullable=True)

class Team(db.Model):
    __tablename__ = 'teams'
    team_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    speaker_1 = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'))
    speaker_2 = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'))
    team_points = db.Column(db.Integer, default=0)

    # Устанавливаем связи с пользователями
    speaker_1_user = db.relationship('User', foreign_keys=[speaker_1], backref='team_speaker_1', lazy=True)
    speaker_2_user = db.relationship('User', foreign_keys=[speaker_2], backref='team_speaker_2', lazy=True)

class Game(db.Model):
    __tablename__ = 'games'
    game_id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(255), nullable=False)
    max_participants = db.Column(db.Integer, nullable=False)
    game_date = db.Column(db.Date, nullable=False)
    game_time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    judge_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'))
    winner_team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id', ondelete='SET NULL'), nullable=True)
    is_finished = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.tournament_id', ondelete='SET NULL'), nullable=True)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.league_id', ondelete='SET NULL'), nullable=True)

    winner_team = db.relationship('Team', backref='games', passive_deletes=True)
    judge = db.relationship('User', backref='judged_games', passive_deletes=True)


class Event(db.Model):
    __tablename__ = 'events'
    event_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.Date, nullable=False)
    event_time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(255))
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_stopped = db.Column(db.Boolean, default=False)  # Новое поле

class EventRegistration(db.Model):
    __tablename__ = 'event_registrations'
    registration_id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'))
    team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id', ondelete='SET NULL'), nullable=True)  # nullable=True
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)


class Result(db.Model):
    __tablename__ = 'results'
    result_id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.game_id', ondelete='CASCADE'))
    team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id', ondelete='CASCADE'))
    score = db.Column(db.Integer, nullable=False)

class League(db.Model):
    __tablename__ = 'leagues'
    league_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class Notification(db.Model):
    __tablename__ = 'notifications'
    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'))
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class EventNotification(db.Model):
    __tablename__ = 'event_notifications'
    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id', ondelete='CASCADE'))
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
