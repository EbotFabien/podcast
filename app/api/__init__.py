import random
import uuid
from flask import Blueprint, url_for
from flask_restx import Api, Resource, fields, reqparse, marshal
from flask import Blueprint, render_template, abort, request, session
from flask_cors import CORS
from functools import wraps
from flask import current_app as app
import requests
from .v1 import web,builder
from app.models import User
import jwt
from datetime import datetime, timedelta
from datetime import datetime
from app import db
from app.services import mail
# API security
authorizations = {
    'KEY': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'API-KEY'
    }
}


# The token decorator to protect my routes
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

'''class MyApi(Api):
    @property
    def specs_url(self):
        """Monkey patch for HTTPS"""
        scheme = 'http' if '8055' in self.base_url else 'https'
        url=url_for(self.endpoint('specs'), _external=True)
        prefix=url.split('/swagger.json')[0]
        prefix=prefix.split('/api')[0]
        url=prefix +'/edlgateway'+'/swagger.json'
        return  url'''

    
api = Blueprint('api', __name__, template_folder = '../templates')
apisec = Api( app=api, doc='/docs', version='1.9.0', title='MikroticA.', \
    description='This documentation contains all routes to access the Mikrotic. \npip install googletransSome routes require authorization and can only be gotten \
    from the Podcast company', license='../LICENSE', license_url='www.sweep.com', contact='touchone0001@gmail.com', authorizations=authorizations)

CORS(api, resources={r"/api/*": {"origins": "*"}})

apisec.add_namespace(web)
apisec.add_namespace(builder)

login = apisec.namespace('/api/auth', \
    description='This contains routes for core app data access. Authorization is required for each of the calls. \
    To get this authorization, please contact out I.T Team ', \
    path='/v1/')

signup = apisec.namespace('/api/auth', \
    description='This contains routes for core app data access. Authorization is required for each of the calls. \
    To get this authorization, please contact out I.T Team ', \
    path='/v1/')

full_login =  apisec.model('full_login', {
    'email': fields.String(required=True, description="Email"),
    'password': fields.String(required=True, description="Users Password"),
})

signupdata = apisec.model('Signup', {
    "email":fields.String(required=False, description="Users Email"),
    "user_name":fields.String(required=False, description="Users Name"),
    "code":fields.String(required=False, description="code"),
    "password": fields.String(required=True, description="Users Password"),
})

@login.doc(
    params={},

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
@login.route('/auth/login')
class Login(Resource):
    @login.expect(full_login)
    def post(self):
        app.logger.info('User login with user_name')
        req_data = request.get_json()
        username=req_data['email']
        password=req_data['password']
        if username and password:
            user=User.query.filter_by(email=username).first()
            if user:
                if user.verify_password(password):
                    token = jwt.encode({
                        'id': user.id,
                        'user': user.email,
                        'exp': datetime.utcnow() + timedelta(days=30),
                        'iat': datetime.utcnow()
                    },
                        app.config.get('SECRET_KEY'),
                        algorithm='HS256')
                    data={
                        'id':user.id,
                        'username':user.username,
                        'email':user.email,
                    }

                    return {
                        'status': 1,
                        'res': 'success',
                        'token': str(token),
                        'data':data
                    }, 200

                else:
                    return {
                        'status': 0,
                        'res':'Wrong password'
                        
                    }, 400
            else:
                    return {
                        'status': 0,
                        'res':'User doesnt exist'
                        
                    }, 400

@signup.doc(
    security='KEY',
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
@signup.route('/auth/signup')
class Signup(Resource):
    #@token_required
    @signup.expect(signupdata)
    def post(self):
        signup_data = request.get_json()
        if signup_data:
            # lang
            username = signup_data['user_name'] or None
            email1 = signup_data['email']
            password = signup_data['password'] or None
            code = signup_data['code'] or None
            email = User.query.filter_by(email=email1).first()
            user = User.query.filter_by(username=username).first()
            if code is not None:
                
                if user.verified == False:
                    if user.code == code : #and user.code_expires_in < datetime.now() :
                        
                        user.verified = True
                        user.user_visibility = True
                        db.session.commit()
                        #mail.welcome_email(user.email,user.username)
                        token = jwt.encode({
                            'user': user.username,
                            'uuid': user.uuid,
                            'exp': datetime.utcnow() + timedelta(days=30),
                            'iat': datetime.utcnow()
                        },
                            app.config.get('SECRET_KEY'),
                            algorithm='HS256')
                        data={
                            'uuid':user.uuid,
                            'id':user.id,
                            'username':user.username,
                            #'profile_picture':user.picture ,
                            #'email':user.email,
                            
                        }
                        return {'status': 1,
                                    'res': 'success',
                                    'uuid': user.uuid,
                                    'token': str(token),
                                    'data':data
                                },200
                    else:
                        return {
                        'status': 0,
                        'res': 'Code has been taken'
                    }, 404
                else:
                    return {
                        'status': 0,
                        'res': 'Code has been sent'
                    }, 404
            if email is not None:
                return {
                    'status': 1,
                    'res': 'email is taken'
                }, 200
            if user is not None:
                return {
                    'status': 2,
                    'res': 'user_name is taken'
                }, 200
            datecreated=datetime.utcnow()
            new=User(username, email1, password,None,datecreated, '', '')
            db.session.add(new)
            new.code=int(random.randrange(100000, 999999))
            db.session.commit()
            
            #mail.verify_email(email1,new.code)
            return {
                'status':new.code,
                'res': 'please verify your account'
            }, 200

        else:
            return {
                'status': 0,
                'res': 'No data'
            }, 201

        
