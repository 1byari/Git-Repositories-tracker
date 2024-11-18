# pylint: disable=C0115

from . import db


class UserModel(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    repos = db.relationship('RepoModel', secondary='user_repository', back_populates='users')

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


class RepoModel(db.Model):
    __tablename__ = 'repository'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    last_synced = db.Column(db.DateTime, nullable=True)

    users = db.relationship('UserModel', secondary='user_repository', back_populates='repos')
    events = db.relationship('EventModel', backref='repository')

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


class UserRepoModel(db.Model):
    __tablename__ = 'user_repository'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    repo_id = db.Column(db.Integer, db.ForeignKey('repository.id'), primary_key=True)


class EventModel(db.Model):
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String)
    created_at = db.Column('created_at', db.DateTime)

    repository_id = db.Column(db.Integer, db.ForeignKey('repository.id'), nullable=False)

    