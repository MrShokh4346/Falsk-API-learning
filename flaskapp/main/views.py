from flaskapp.models import Video
from flaskapp.schemas import VideoSchema
from flaskapp import app, logger, docs
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_apispec import use_kwargs, marshal_with

videos = Blueprint('videos', __name__)


@videos.route('/api', methods=['GET'])
@jwt_required()
@marshal_with(VideoSchema(many=True))
def get_video():
    try:
        user_id = get_jwt_identity()
        videos = Video.get_videos()
        return videos
    except Exception as e:
        logger.warning(f'user: {user_id} api - read action failed with error: {e}')
        return jsonify({"message":str(e)}), 400
    

@videos.route('/api', methods=['POST'])
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


@videos.route('/api/<int:id>', methods=['GET'])
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


@videos.route('/api/<int:id>', methods=['PUT'])
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


@videos.route('/api/<int:id>', methods=['DELETE'])
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


@videos.errorhandler(422)
def error_handler(err):
    header = err.data.get('handler', None)
    messages = err.data.get('messages', ['Invalid input'])
    logger.warning(f'Invalid input error: {messages}')
    if header:
        return {"meaasges":messages}, 400, header
    else:
        return {"meaasges":messages}, 400

docs.register(get_video, blueprint='videos')
docs.register(new_video, blueprint='videos')
docs.register(get_one_video, blueprint='videos')
docs.register(update_video, blueprint='videos')
docs.register(delete_video, blueprint='videos')



