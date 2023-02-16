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
import logging

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


def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    file_handler = logging.FileHandler('log/api.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()


@app.route('/register', methods = ['POST'])
@use_kwargs(UserSchema)
@marshal_with(AuthenticateSchema)
def register(**kwargs):
    try:
        user = User.query.filter_by(email=kwargs['email']).first()
        if not user:
            user = User(**kwargs)
            db.session.add(user)
            db.session.commit()
            token = user.get_token()
            return jsonify({'access_token':token})
        else:
            return jsonify({"message":"this email already exists"})
    except Exception as e:
        logger.warning(f'registration action failed with error: {e}')
        return {"message":str(e)}, 400

@app.route('/login', methods = ['POST'])
@use_kwargs(UserSchema(only=('email', 'password')))
@marshal_with(AuthenticateSchema)
def login(**kwargs):
    try:
        user = User.authenticate(**kwargs)
        token = user.get_token()
        return jsonify({'access_token':token})
    except Exception as e:
        logger.warning(f'login action failed with email: {kwargs["email"]} with error: {e}')
        return {"message":str(e)}, 400


@app.route('/api', methods=['GET'])
@jwt_required()
@marshal_with(VideoSchema(many=True))
def get_video():
    try:
        user_id = get_jwt_identity()
        videos = Video.get_videos(user_id)
        return videos
    except Exception as e:
        logger.warning(f'user: {user_id} api - read action failed with error: {e}')
        return jsonify({"message":str(e)}), 400
    

@app.route('/api', methods=['POST'])
@jwt_required()
@use_kwargs(VideoSchema)
@marshal_with(VideoSchema)
def new_video(**kwargs):
    try:
        user_id = get_jwt_identity()
        video = Video(user_id=user_id, **kwargs)
        video.save()
        return video, 201
    except Exception as e:
        logger.warning(f'user: {user_id} api - add action failed with error: {e}')
        return {"message":str(e)}, 400


@app.route('/api/<int:id>', methods=['GET'])
@jwt_required()
@marshal_with(VideoSchema())
def get_one_video(id):
    try:
        user_id = get_jwt_identity()
        video = Video.get(user_id,id)
        if not video:
            return {"message":"No video with this id"}, 404  
        return video, 200
    except Exception as e:
        logger.warning(f'user: {user_id} api id:{id} - read action failed with error: {e}')
        return {"message":str(e)}, 400


@app.route('/api/<int:id>', methods=['PUT'])
@jwt_required()
@use_kwargs(VideoSchema)
@marshal_with(VideoSchema)
def update_video(id, **kwargs):
    try:
        user_id = get_jwt_identity()
        video = Video.get(user_id, id)
        video.update(**kwargs)
        return video, 200
    except Exception as e:
        logger.warning(f'user: {user_id} api id:{id} - update action failed with error: {e}')
        return {"message":str(e)}, 400


@app.route('/api/<int:id>', methods=['DELETE'])
@jwt_required()
@marshal_with(VideoSchema)
def delete_video(id):
    try:
        user_id = get_jwt_identity()
        video = Video.get(user_id, id)
        video.delete()
        return '', 204
    except Exception as e:
        logger.warning(f'user: {user_id} api id:{id} - delete action failed with error: {e}')
        return {"message":str(e)}, 400


@app.errorhandler(422)
def error_handler(err):
    header = err.data.get('handler', None)
    messages = err.data.get('messages', ['Invalid input'])
    logger.warning(f'Invalid input error: {messages}')
    if header:
        return {"meaasges":messages}, 400, header
    else:
        return {"meaasges":messages}, 400


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


docs.register(register)
docs.register(login)
docs.register(get_video)
docs.register(new_video)
docs.register(get_one_video)
docs.register(update_video)
docs.register(delete_video)


if __name__ == '__main__':
    app.run(debug=1)
