import json
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
from app.models import Profile,Album,User,Episode,Episode_script
from app import db
import cloudinary
import cloudinary.uploader
from werkzeug.datastructures import FileStorage
from config import Config


cloudinary.config(
    cloud_name="odaaay",
    api_key="893419336671437",
    api_secret="lIGoIkb5l7vZGpcD-k18Py49nGQ"
)

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
builder1=Api( app=api, doc='/docs',version='1.4',title='AMS',\
description='', authorizations=authorizations)
#implement cors

CORS(api, resources={r"/api/*": {"origins": "*"}})

uploader = builder1.parser()
uploader.add_argument('file', location='files', type=FileStorage,
                      required=False, help="You must parse a file")
uploader.add_argument('name', location='form', type=str,
                      required=False, help="Name cannot be blank")

builder  = builder1.namespace('/api/builder', \
    description= "All routes under this section of the documentation are the open routes bots can perform CRUD action \
    on the application.", \
    path = '/v1/')


Album_ = builder.model('Album', {
    "price": fields.String(required=False,default=" ", description="Users nom"),
    "min_age":fields.String(required=False,default=" ", description="Users prenom"),
    "pic_url":fields.String(required=False,default=" ", description="Users Email"),
    "date_created":fields.String(required=False,default=" ", description="Users Phone"),
    "title":fields.String(required=False,default=" ", description="Users login"),
    "description":fields.String(required=False,default=" ", description="Users role"),
    "author":fields.String(required=False,default=" ", description="Users role"),

})

Episode_ = builder.model('Episode', {
    "name": fields.String(required=False,default=" ", description="Users nom"),
    "album":fields.Integer(required=False,default=" ", description="Album id"),
    "Interactive":fields.Boolean(required=False,default=False, description="Interactive or Not"),
    "orig_name":fields.String(required=False,default=" ", description="Original file name"),
    "link":fields.String(required=False,default=" ", description="Original file link"),
    "profile":fields.String(required=False,default=" ", description="Profile"),
})

get_Episode = builder.model('get_Episode', {
    'id':fields.Integer,
    "name": fields.String(required=False,default=" ", description="Users nom"),
    "album":fields.Integer(required=False,default=" ", description="Album id"),
    "Interactive":fields.Boolean(required=False,default=False, description="Interactive or Not"),
    "orig_name":fields.String(required=False,default=" ", description="Original file name"),
    "link":fields.String(required=False,default=" ", description="Original file link"),
})

get_Album = builder.model('Get_Album', {
    'id':fields.Integer,
    "price": fields.String(required=False,default=" ", description="Users nom"),
    "min_age":fields.String(required=False,default=" ", description="Users prenom"),
    "pic_url":fields.String(required=False,default=" ", description="Users Email"),
    "date_created":fields.String(required=False,default=" ", description="Users Phone"),
    "title":fields.String(required=False,default=" ", description="Users login"),
    "description":fields.String(required=False,default=" ", description="Users role"),
    "public":fields.Boolean(required=False,default=" ", description="Users role"),
    "author":fields.Integer(required=False,default=" ", description="Users role"),
})

Script_ = builder.model('Script', {
    "episode": fields.String(required=False,default=" ", description="Episode")
})

get_Script = builder.model('get_Script', {
    "id":fields.Integer,
    "data" : fields.String(required=False,default=" ", description="Episode"),
    "user": fields.String(required=False,default=" ", description="Episode"),
    "profile": fields.String(required=False,default=" ", description="Episode"),
    "lastupdated": fields.String(required=False,default=" ", description="Episode"),
    "dateuploaded": fields.String(required=False,default=" ", description="Episode"),
    "episode_id":fields.Integer
})



@builder.doc(
    security='KEY',
    params={'start': 'Value to start from ',
             'limit': 'Total limit of the query',
             'count': 'Number results per page',
             'lang': 'Language'
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
@builder.route('/upload')
class Upl(Resource):
    @token_required
    @builder.expect(uploader)
    def post(self):
        args = uploader.parse_args()
        destination = Config.UPLOAD_FOLDER_MEDIA
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
       
        File = args['file']
        Name = args['name']
        if File.mimetype == "image/jpeg":
            fila = os.path.join(destination, str(
                data['uuid']), 'post')  # ,Name)
            if os.path.isdir(fila) == False:
                os.makedirs(fila)
            fil = os.path.join(fila, Name)  # ,Name)
            File.save(fil)
            upload_result = cloudinary.uploader.upload('https://odaaay.com/api/static/files/'+str(data['uuid'])+"/post/"+Name)
            return {
                "status": 1,
                "thumb_url":upload_result["secure_url"], #str(data['uuid'])+"/post/"+Name,
            }, 200

        if File.mimetype == "image/jpg":
            fila = os.path.join(destination, str(
                data['uuid']), 'post')  # ,Name)
            if os.path.isdir(fila) == False:
                os.makedirs(fila)
            fil = os.path.join(fila, Name)  # ,Name)
            File.save(fil)
            upload_result = cloudinary.uploader.upload('https://odaaay.com/api/static/files/'+str(data['uuid'])+"/post/"+Name)
            return {
                "status": 1,
                "thumb_url":upload_result["secure_url"], #str(data['uuid'])+"/post/"+Name,
            }, 200
        else:
            return {
                "status": 0,
                "res": "Put a Jpeg file",
            }, 200
        

@builder.doc(
    security='KEY',
    params={ 'start': 'Value to start from '
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
@builder.route('/builder/add/album')

class Album_add(Resource):
    @token_required
    @builder.expect(Album_)
    def post(self):
        token = request.headers['API-KEY']
        data = jwt.decode(token,app.config.get('SECRET_KEY'),algorithms='HS256')
        user= User.query.filter_by(uuid=data['uuid']).first()
        profile= Profile.query.filter_by(id=req_data['author']).first()
        req_data = request.get_json()
        
        if user.id == profile.user_id:
            album=Album(req_data['price'], req_data['min_age'],req_data['pic_url'],req_data['author'],req_data['title'],req_data['description'],req_data['public'])
            db.session.add(album)
            db.session.commit()
            return {
                'data':marshal(album,get_Album),
                'res':'Album uploaded'
            },200

@builder.doc(
    security='KEY',
    params={'uuid': 'Identity of User'
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
@builder.route('/builder/all/user/single/album')
class all_user_single_album(Resource):
    @token_required
    def get(self):
        if request.args:
            token = request.headers['API-KEY']
            #uuid = request.args.get('uuid')
            data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
            user= User.query.filter_by(id=data['id']).first()
            profile=Profile.query.filter_by(user_id=user.id).all()
            if user:
                if profile:
                    album=Album.query.filter_by(author=profile.id).all()
                    return {
                        "results": marshal(album,get_Album)
                    }, 200
                else:
                    return {
                   
                    "results": 'Profile not found'
                    }, 400
            else:
                return {
                   
                    "results": 'user not found'
                }, 400
            

@builder.doc(
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
@builder.route('/builder/all/album')
class all_album(Resource):
    @token_required
    def get(self):
        if request.args:
            token = request.headers['API-KEY']
            data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
            user= User.query.filter_by(id=data['id']).first()
    
            if user:
                
                album=Album.query.all()
                return {
                    "results": marshal(album,get_Album)
                }, 200
                
            else:
                return {
                   
                    "results": 'user not found'
                }, 400


@builder.doc(
    security='KEY',
    params={'uuid': 'UUID of User',
            'album':'Identity of album'
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
@builder.route('/builder/user/single/album')
class user_single_album(Resource):
    @token_required
    def get(self):
        if request.args:
            token = request.headers['API-KEY']
            #uuid = request.args.get('uuid')
            album = request.args.get('album')
            data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
            user= User.query.filter_by(id=data['id']).first()
            profile=Profile.query.filter_by(user_id=user.id).all()
            if user:
                if profile:
                    album_data=Album.query.filter(and_(Album.id==album,Album.author==profile.id)).first()
                    return {
                        "results": marshal(album_data,get_Album)
                    }, 200
                else:
                    return {
                   
                    "results": 'Profile not found'
                    }, 400
            else:
                return {
                   
                    "results": 'user not found'
                }, 400



@builder.doc(
    security='KEY',
    params={ 'start': 'Value to start from '
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
@builder.route('/builder/add/episode')

class Episode_add(Resource):
    @token_required
    @builder.expect(Episode_)
    def post(self):
        token = request.headers['API-KEY']
        data = jwt.decode(token,app.config.get('SECRET_KEY'),algorithms='HS256')
        user= User.query.filter_by(uuid=data['uuid']).first()
        req_data = request.get_json()
        
        if user:
            if req_data['interactive'] == False:
                episode=Episode(req_data['name'],req_data['album'],req_data['orig_name'],req_data['link'],req_data['interactive'])
                db.session.add(episode)
                db.session.commit()
                return {
                    'data':marshal(episode,get_Episode),
                    'res':'Episode Added'
                },200
            else:
                episode=Episode(req_data['name'],req_data['album'],req_data['orig_name'],req_data['link'],req_data['interactive'])
                db.session.add(episode)
                db.session.commit()
                data=""
                saveepisode = Episode_script(user.name, episode.id, data, req_data['profile'])
                db.session.add(saveepisode)
                db.session.commit()
                return {
                    'data':marshal(episode,get_Episode),
                    'res':'Episode Added'
                },200



@builder.doc(
    security='KEY',
    params={ 'start': 'Value to start from '
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
@builder.route('/builder/add/episode')

class Episode_add(Resource):
    @token_required
    @builder.expect(Script_)
    def post(self):
        token = request.headers['API-KEY']
        data = jwt.decode(token,app.config.get('SECRET_KEY'),algorithms='HS256')
        user= User.query.filter_by(uuid=data['uuid']).first()
        req_data = request.get_json()
        script=Episode_script.query.filter_by(id=req_data['episode'])
        if user:
                script.data=json.dumps(req_data['data'])
                db.session.commit()
                return {
                    'data':marshal(script,get_Script),
                    'res':'Episode Script uploaded'
                },200








@builder.doc(
    security='KEY',
    params={'uuid': 'UUID of User',
            'album':'Identity of album'
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
@builder.route('/builder/user/single/album/episodes')
class user_single_album_episodes(Resource):
    @token_required
    def get(self):
        if request.args:
            token = request.headers['API-KEY']
            #uuid = request.args.get('uuid')
            album = request.args.get('album')
            data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
            user= User.query.filter_by(id=data['id']).first()
            
            if user:
                    all_episode=Episode.query.filter_by(album_id=int(album)).first()
                    return {
                        "results": marshal(all_episode,get_Episode)
                    }, 200
                
            else:
                return {
                   
                    "results": 'user not found'
                }, 400


@builder.doc(
    security='KEY',
    params={
            'episode':'Identity of episode'
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
@builder.route('/builder/episode/script')
class all_album(Resource):
    @token_required
    def get(self):
        if request.args:
            token = request.headers['API-KEY']
            episode = request.args.get('episode')
            data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
            user= User.query.filter_by(id=data['id']).first()
            Episod=Episode.query.filter_by(id=int(episode)).first()
            if user:
                if Episod:
                    script=Episode_script.query.filter_by(episode_id=int(episode)).first()
                    if script:

                        return {
                            "results": marshal(script,get_Script)
                        }, 200
                    else:
                        return {
                        
                            "results": 'Script not found'
                        }, 400
                
            else:
                return {
                   
                    "results": 'user not found'
                }, 400