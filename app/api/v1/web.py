from flask_restx import Namespace, Resource, fields,marshal,Api
import jwt, uuid, os
from flask_cors import CORS
from functools import wraps 
from flask import abort, request, session,Blueprint
from datetime import datetime
from flask import current_app as app
#from sqlalchemy import or_, and_, distinct, func
#from project import cache  #, logging
import requests
from app import db
from app.models import User,Profile




authorizations = {
    'KEY': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'API-KEY'
    }
}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'API-KEY' in request.headers:
            token = request.headers['API-KEY']
            try:
                data = jwt.decode(token, app.config.get('SECRET_KEY'))
            except:
                return {'message': 'Token is invalid.'}, 403
        if not token:
            return {'message': 'Token is missing or not found.'}, 401
        if data:
            pass
        return f(*args, **kwargs)
    return decorated

api = Blueprint('api',__name__, template_folder='../templates')
web1=Api( app=api, doc='/docs',version='1.4',title='AMS',\
description='', authorizations=authorizations)
#implement cors

CORS(api, resources={r"/api/*": {"origins": "*"}})

web  = web1.namespace('/api/web', \
    description= "All routes under this section of the documentation are the open routes bots can perform CRUD action \
    on the application.", \
    path = '/v1/')


prof = web.model('Profile', {
    'name': fields.String,
    'age': fields.Integer,
    'bio': fields.String,
})

get_prof = web.model('Get_Profile', {
    'id':fields.Integer,
    'name': fields.String,
    'age': fields.Integer,
    'bio': fields.String,
})

@web.doc(
    security='KEY',
    params={ 'start': 'Value to start from ',
            'limit': 'Total limit of the query',
            'count': 'Number results per page',
            'lang' : 'Language'
            },
    responses={
        200: 'ok',
        201: 'created',
        204: 'No Content',
        301: 'Resource was moved',
        304: 'Resource was not Modified',
        400: 'Bad Request to server',
        401: 'Unauthorized request from client to server',
        403: 'Forbidden request from client to server',
        404: 'Resource Not found',
        500: 'internal server error, please contact admin and report issue'
    })
@web.route('/user/add/profile')

class profile(Resource):
    @token_required
    @web.expect(prof)
    def post(self):
        token = request.headers['API-KEY']
        data = jwt.decode(token,app.config.get('SECRET_KEY'),algorithms='HS256')
        user= User.query.filter_by(uuid=data['uuid']).first()
        req_data = request.get_json()
        
        if user:
            prof=Profile(user_id=user.id,bio=req_data['bio'],age=req_data['age'])
            db.session.add(prof)
            db.session.commit()
            return {
                'data':marshal(prof,get_prof),
                'res':'profile Created'
            },200


@web.doc(
    security='KEY',
    params={
            },
    responses={
        200: 'ok',
        201: 'created',
        204: 'No Content',
        301: 'Resource was moved',
        304: 'Resource was not Modified',
        400: 'Bad Request to server',
        401: 'Unauthorized request from client to server',
        403: 'Forbidden request from client to server',
        404: 'Resource Not found',
        500: 'internal server error, please contact admin and report issue'
    })
@web.route('/user/all/single/profile')
class all_single_user_profile(Resource):
    @token_required
    def get(self):
        if request.args:
            token = request.headers['API-KEY']
            data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
            user= User.query.filter_by(id=data['id']).first()
            if user:
                profile=Profile.query.filter_by(user_id=user.id).all()
                return {
                    "results": marshal(profile,get_prof)
                }, 200
            else:
                return {
                   
                    "results": 'user not found'
                }, 400
            


@web.doc(
    security='KEY',
    params={'ID': 'Identity of profile'
            },
    responses={
        200: 'ok',
        201: 'created',
        204: 'No Content',
        301: 'Resource was moved',
        304: 'Resource was not Modified',
        400: 'Bad Request to server',
        401: 'Unauthorized request from client to server',
        403: 'Forbidden request from client to server',
        404: 'Resource Not found',
        500: 'internal server error, please contact admin and report issue'
    })
@web.route('/user/single/profile')
class user_single_profile(Resource):
    @token_required
    def get(self):
        if request.args:
            token = request.headers['API-KEY']
            pro = request.args.get('ID')
            data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
            user= User.query.filter_by(id=data['id']).first()
            if user:
                profile=Profile.query.filter(and_(Profile.id==pro,Profile.user_id==user.id)).all()
                return {
                    "results": marshal(profile,get_prof)
                }, 200
            else:
                return {
                   
                    "results": 'user not found'
                }, 400


