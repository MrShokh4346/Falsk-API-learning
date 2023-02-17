from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec import APISpec
from flask_apispec.extension import FlaskApiSpec
from flask import  jsonify, request

import logging


app = Flask(__name__)
app.config['SECRET_KEY']='SECRET_KEY'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///flask_vazifa.db"
db = SQLAlchemy()
migrate = Migrate(app, db)
jwt = JWTManager()
docs = FlaskApiSpec()


app.config.update({
    'APISPEC_SPEC':APISpec(
        title='videoblog',
        version='v1',
        openapi_version='2.0',
        plugins=[MarshmallowPlugin()],
    ),
    'APISPEC_SWAGGER_URL' : '/swagger/'
})

db.init_app(app)

# from . import Users, Videos

# with app.app_context():
#     db.create_all()
#     db.session.commit()


def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    file_handler = logging.FileHandler('log/api.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()


from .main.views import videos
from .users.views import users

app.register_blueprint(videos)
app.register_blueprint(users)

docs.init_app(app)
jwt.init_app(app)
