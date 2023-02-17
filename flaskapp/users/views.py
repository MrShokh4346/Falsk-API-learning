from flaskapp.models import User
from flaskapp.schemas import UserSchema, AuthenticateSchema, UsersListSchema
from flaskapp import app
from flask import Blueprint, jsonify
from flask_apispec import use_kwargs, marshal_with
from flask_jwt_extended import get_jwt_identity, jwt_required
from flaskapp import logger, docs

users = Blueprint('users', __name__)



@users.route('/users', methods=['GET'])
@jwt_required()
@marshal_with(UsersListSchema(many=True))
def get_video():
    try:
        user_id = get_jwt_identity()
        users = User.query.all()
        return users
    except Exception as e:
        logger.warning(f'user: {user_id} users - read action failed with error: {e}')
        return jsonify({"message":str(e)}), 400


@users.route('/register', methods = ['POST'])
@use_kwargs(UserSchema)
@marshal_with(AuthenticateSchema)
def register(**kwargs):
    try:
        user = User.query.filter_by(email=kwargs['email']).first()
        if not user:
            user = User(**kwargs)
            user.save()
            token = user.get_token()
            return jsonify({'access_token':token})
        else:
            return jsonify({"message":"this email already exists"})
    except Exception as e:
        logger.warning(f'registration action failed with error: {e}')
        return {"message":str(e)}, 400

@users.route('/login', methods = ['POST'])
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


@users.errorhandler(422)
def error_handler(err):
    header = err.data.get('handler', None)
    messages = err.data.get('messages', ['Invalid input'])
    logger.warning(f'Invalid input error: {messages}')
    if header:
        return {"meaasges":messages}, 400, header
    else:
        return {"meaasges":messages}, 400


docs.register(register, blueprint='users')
docs.register(login, blueprint='users')
