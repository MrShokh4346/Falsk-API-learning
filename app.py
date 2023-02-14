# from __init__ import app, db
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required

from flask import  jsonify, request
# from models import User

from flask_jwt_extended import create_access_token
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SECRET_KEY']='f1640035e2804809953c06ee89d76123'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///flask_vazifa.db"
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)



@app.route('/register', methods = ['POST'])
def register():
    params = request.json
    user = User.query.filter_by(email=params['email']).first()
    if not user:
        user = User(**params)
        db.session.add(user)
        db.session.commit()
        token = user.get_token()
        return jsonify({'access_token':token})
    else:
        return jsonify({"msg":"this email already exists"})

@app.route('/login', methods = ['POST'])
def login():
    params = request.json
    user = User.authenticate(**params)
    token = user.get_token()
    return jsonify({'access_token':token})



@app.route('/api', methods=['GET'])
@jwt_required()
def get_video():
    user_id = get_jwt_identity()
    videos = Video.query.filter_by(user_id=user_id)
    serialized = []
    for video in videos:
        serialized.append({
            "id" : video.id,
            "name" : video.name,
            "description" : video.description
        })
    return jsonify(serialized)


@app.route('/api', methods=['POST'])
@jwt_required()
def new_video():
    user_id = get_jwt_identity()
    params = request.json
    video = Video(user_id=user_id, **params)
    db.session.add(video)
    db.session.commit()
    serialized = {
        "id" : video.id,
        "name" : video.name,
        "description" : video.description
    }
    return jsonify(serialized), 201


@app.route('/api/<int:id>', methods=['GET'])
@jwt_required()
def get_one_video(id):
    user_id = get_jwt_identity()
    video = Video.query.filter(Video.user_id==user_id, Video.id==id).first()
    serialized = []
    serialized.append({
        "id" : video.id,
        "name" : video.name,
        "description" : video.description
    })
    return jsonify(serialized), 200


@app.route('/api/<int:id>', methods=['PUT'])
@jwt_required()
def update(id):
    user_id = get_jwt_identity()
    video = Video.query.filter(Video.user_id==user_id, Video.id==id).first()
    params = request.json
    if not video:
        return jsonify({"msg" : "No video with this id"}), 400
    for key, value in params.items():
        setattr(video, key, value)
    db.session.commit()
    serialized = []
    serialized.append({
        "id" : video.id,
        "name" : video.name,
        "description" : video.description
    })
    return jsonify(serialized), 200


@app.route('/api/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_video(id):
    user_id = get_jwt_identity()
    video = Video.query.filter(Video.user_id==user_id, Video.id==id).first()
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
        print(user.email)
        print(email)
        print(password)
        if not check_password_hash(user.password, password):
            raise Exception('No user with this password')
        return user


with app.app_context():
    db.create_all()
    db.session.commit()


if __name__ == '__main__':
    app.run(debug=1)