# from app import app, db
# from flask_jwt_extended import create_access_token
# from datetime import timedelta
# from werkzeug.security import generate_password_hash, check_password_hash



# class Video(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     name = db.Column(db.String(50), nullable=False)
#     description = db.Column(db.String(255), nullable=False)


# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), nullable=False)
#     email = db.Column(db.String(50), unique=True, nullable=False)
#     password = db.Column(db.String(128))
#     videos = db.relationship('Video', backref='owner')

#     def __init__(self, **kwargs):
#         self.name = kwargs.get('name')
#         self.email = kwargs.get('email')
#         self.password = generate_password_hash(kwargs.get('password'))

#     def get_token(self, expire_time=24):
#         expire_delte = timedelta(expire_time)
#         token = create_access_token(
#             identity=self.id, expires_delta=expire_delte
#         )
#         return token

#     @classmethod
#     def authenticate(cls, email, password):
#         user = cls.query.filter(cls.email==email).first()
#         if not check_password_hash(user.password, password):
#             raise Exception('No user with this password')
#         return user


# with app.app_context():
#     db.create_all()
#     db.session.commit()

