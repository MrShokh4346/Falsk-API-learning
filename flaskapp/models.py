from . import app, db
from flask_jwt_extended import create_access_token
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=False)

    @classmethod
    def get_videos(cls, user_id):
        try:
            videos = cls.query.filter(cls.user_id==user_id)
            if not videos:
                raise Exception('You do not have any video')
            return videos
        except Exception:
            db.session.rollback()
            raise
    
    @classmethod
    def get(cls, user_id, id):
        try:
            video = cls.query.filter(cls.user_id==user_id, cls.id==id).first()
            if not video:
                raise Exception('No video with this id')
            return video
        except Exception:
            db.session.rollback()
            raise

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
    
    def update(self, **kwargs):
        try:
            for key, value in kwargs.items():
                setattr(self, key, value)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128))
    videos = db.relationship('Video', backref='owner')

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.email = kwargs.get('email')
        self.password = generate_password_hash(kwargs.get('password'))

    def get_token(self, expire_time=24):
        expire_delte = timedelta(expire_time)
        token = create_access_token(
            identity=self.id, expires_delta=expire_delte
        )
        return token

    @classmethod
    def authenticate(cls, email, password):
        user = cls.query.filter(cls.email==email).first()
        if user:
            if not check_password_hash(user.password, password):
                raise Exception('No user with this password')
        else:
            raise Exception('No user with this email')
        return user


with app.app_context():
    db.create_all()
    db.session.commit()