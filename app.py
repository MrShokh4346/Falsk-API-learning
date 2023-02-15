# from __init__ import app, db
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec import APISpec
from flask_apispec.extension import FlaskApiSpec
from flask import  jsonify, request
from flask_apispec import use_kwargs, marshal_with
from schemas import VideoSchema, UserSchema, AuthenticateSchema

from flask_jwt_extended import create_access_token
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash




app = Flask(__name__)
app.config['SECRET_KEY']='SECRET_KEY'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///flask_vazifa.db"
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
docs = FlaskApiSpec()

docs.init_app(app)

app.config.update({
    'APISPEC_SPEC':APISpec(
        title='videoblog',
        version='v1',
        openapi_version='2.0',
        plugins=[MarshmallowPlugin()],
    ),
    'APISPEC_SWAGGER_URL' : '/swagger/'
})


@app.route('/register', methods = ['POST'])
@use_kwargs(UserSchema)
@marshal_with(AuthenticateSchema)
def register(**kwargs):
    user = User.query.filter_by(email=kwargs['email']).first()
    if not user:
        user = User(**kwargs)
        db.session.add(user)
        db.session.commit()
        token = user.get_token()
        return jsonify({'access_token':token})
    else:
        return jsonify({"message":"this email already exists"})

@app.route('/login', methods = ['POST'])
@use_kwargs(UserSchema(only=('email', 'password')))
@marshal_with(AuthenticateSchema)
def login():
    params = request.json
    user = User.authenticate(**params)
    token = user.get_token()
    return jsonify({'access_token':token})



@app.route('/api', methods=['GET'])
@jwt_required()
@marshal_with(VideoSchema(many=True))
def get_video():
    user_id = get_jwt_identity()
    videos = Video.query.filter(Video.user_id==user_id)
    return videos

@app.route('/api', methods=['POST'])
@jwt_required()
@use_kwargs(VideoSchema)
@marshal_with(VideoSchema)
def new_video(**kwargs):
    user_id = get_jwt_identity()
    video = Video(user_id=user_id, **kwargs)
    db.session.add(video)
    db.session.commit()
    return video, 201


@app.route('/api/<int:id>', methods=['GET'])
@jwt_required()
@marshal_with(VideoSchema())
def get_one_video(id):
    user_id = get_jwt_identity()
    video = Video.query.filter(Video.user_id==user_id, Video.id==id).first()
    return video, 200


@app.route('/api/<int:id>', methods=['PUT'])
@jwt_required()
@use_kwargs(VideoSchema)
@marshal_with(VideoSchema)
def update(id, **kwargs):
    user_id = get_jwt_identity()
    video = Video.query.filter(Video.user_id==user_id, Video.id==id).first()
    if not video:
        return jsonify({"message" : "No video with this id"}), 400
    for key, value in kwargs.items():
        setattr(video, key, value)
    db.session.commit()
    return video, 200


@app.route('/api/<int:id>', methods=['DELETE'])
@jwt_required()
@marshal_with(VideoSchema)
def delete_video(id):
    user_id = get_jwt_identity()
    video = Video.query.filter(Video.user_id==user_id, Video.id==id).first()
    if not video:
        return jsonify({"message" : "No video with this id"}), 400
    db.session.delete(video)
    db.session.commit()
    return '', 204



class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128))
    videos = db.relationship('Video', backref='owner')

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
        if not check_password_hash(user.password, password):
            raise Exception('No user with this password')
        return user


with app.app_context():
    db.create_all()
    db.session.commit()


docs.register(register)
docs.register(login)
docs.register(get_video)
docs.register(new_video)
docs.register(get_one_video)
docs.register(update)
docs.register(delete_video)


if __name__ == '__main__':
    app.run(debug=1)
