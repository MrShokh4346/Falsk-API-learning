from marshmallow import Schema, validate, fields

class VideoSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    name = fields.String(required=True, 
                         validate=[validate.Length(max=50)])
    description = fields.String(required=True, 
                               validate=[validate.Length(max=255)])
    message = fields.String(dump_only=True)

class UserSchema(Schema):
    name = fields.String(required=True, 
                         validate=[validate.Length(max=50)])
    email = fields.String(required=True, 
                         validate=[validate.Length(max=150)])
    password = fields.String(required=True, load_only=True,
                         validate=[validate.Length(max=150)])
    videos = fields.Nested(VideoSchema, dump_only=True, many=True)


class AuthenticateSchema(Schema):
    access_token = fields.String(dump_only=True)
    message = fields.String(dump_only=True)


# class UsersListSchema(Schema):
#     name = fields.String(dump_only=True)
#     email = fields.String(dump_only=True)