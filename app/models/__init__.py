from datetime import datetime
import json
from time import time
from flask import current_app

import jwt
from app import db
from werkzeug.security import generate_password_hash,check_password_hash


from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid

album_sub = db.Table('Albumsub',
    db.Column('profile_id', db.Integer, db.ForeignKey('Profile.id'), primary_key=True),
    db.Column('album_id', db.Integer, db.ForeignKey('Album.id'), primary_key=True)
)

payment_sub = db.Table('Paymentsub',
    db.Column('user_id', db.Integer, db.ForeignKey('User.id'), primary_key=True),
    db.Column('payment_id', db.Integer, db.ForeignKey('Payment.id'), primary_key=True)
)

# The user table will store user all user data, passwords will not be stored
# This is for confidentiality purposes. Take note when adding a model for
# vulnerability.
class User (db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key = True)
    uuid = db.Column(db.String, unique=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    ip_addr = db.Column(db.String)
    verified = db.Column(db.Boolean,default=False)
    verified_on = db.Column(db.DateTime)
    vericount = db.Column(db.Integer, default=0)
    bio = db.Column(db.String)
    code=db.Column(db.String)
    datecreated = db.Column(db.DateTime)
    profile_pic = db.Column(db.String)
    profile_id = db.relationship('Profile', backref='User_profiles', lazy=True)
    purchase_id = db.relationship('Purchase', backref='User_purchase', lazy=True)

    def __init__(self, username, email, password_hash, ip_addr, \
    datecreated, bio, profile_pic):
        self.username = username
        self.uuid = uuid.uuid4().hex
        self.email = email
        self.password_hash =  generate_password_hash(password_hash)
        self.ip_addr = ip_addr
        self.datecreated = datecreated
        self.bio = bio
        self.profile_pic = profile_pic
        self.vericount = 0

    def __repr__(self):
        return '<User %r>' % self.username

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

# The settings model will contain all the settings for a specific user.
# this will have all the general settings too.
class Setting (db.Model):
    __tablename__ = "Setting"
    id = db.Column(db.Integer, primary_key = True)
    download_qty = db.Column(db.String)
    terms = db.Column(db.String, nullable=False)
    version_info = db.Column(db.String, nullable=False)
    publisher_id = db.Column(db.String)
    theme_color = db.Column(db.String)
    public = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('Profile.id'),
        nullable=False, unique=True)

    def __init__(self, download_qty, theme_color, user_id):
        self.download_qty = download_qty
        self.theme_color = theme_color
        self.user_id = user_id
        self.terms = "To be decided"
        self.version_info = "1.0"
        self.public = False
        self.publisher_id = "No publisher"

    def __repr__(self):
        return '<Setting %r>' % self.id

class Profile(db.Model):
    __tablename__ =  "Profile"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    setting_id = db.relationship('Setting', backref='User_setting', lazy=True)
    bio = db.Column(db.String)
    min_age = db.Column(db.String)
    profile_pic = db.Column(db.String)
    follower_id = db.relationship('Follower', backref='User', lazy=True)
    album_id = db.relationship('Album', backref='Profile_album', lazy=True)

    def __init__(self, user_id, name, min_age, bio, profile_pic):
        self.user_id = user_id
        self.name = name
        self.min_age = min_age
        self.bio = bio
        self.profile_pic = profile_pic

    def __repr__(self):
        return '<Profile %r>' % self.id

class Follower(db.Model):
    __tablename__ =  "Follower"
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('Profile.id'),
        nullable=False)

class Notification (db.Model):
    __tablename__ = "Notification"
    id = db.Column(db.Integer, primary_key = True)
    message = db.Column(db.String, nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Boolean, nullable=False)

    def __init__(self, message, datetime, status):
        self.message = message
        self.datetime = datetime
        self.status = status

    def __repr__(self):
        return '<Notification %r>' % self.id

class Achievement (db.Model):
    __tablename__ = "Achievement"
    id = db.Column(db.Integer, primary_key = True)
    ach_type = db.Column(db.String, nullable=False)

class Purchase (db.Model):
    __tablename__ = "Purchase"
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey('Album.id'), nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey('Payment.id'), nullable=False)
    datetime = db.Column(db.DateTime)

class Album (db.Model):
    __tablename__ = "Album"
    id = db.Column(db.Integer, primary_key = True)
    price = db.Column(db.Float)
    min_age = db.Column(db.Integer)
    pic_url = db.Column(db.String)
    datecreated = db.Column(db.DateTime)
    title = db.Column(db.String)
    description = db.Column(db.String)
    public = db.Column(db.Boolean)
    episode_id = db.relationship('Episode', backref='album_episode', lazy=True)
    author = db.Column(db.Integer, db.ForeignKey('Profile.id'), nullable=False)

    def __init__(self, price, min_age, pic_url, author, title, description, public):
        self.price = price
        self.min_age = min_age
        self.pic_url = pic_url
        self.author = author
        self.description = description
        self.title = title
        self.public = public
        self.datecreated = datetime.utcnow()

    def __repr__(self):
        return '<Album %r>' % self.id

class Payment (db.Model):
    __tablename__ = "Payment"
    id = db.Column(db.Integer, primary_key = True)
    payment_type = db.Column(db.String)
    amount = db.Column(db.Float)

class Episode (db.Model):

    __tablename__ = "Episode"
    
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    orig_name = db.Column(db.String)
    audio_url = db.Column(db.String)
    interactive = db.Column(db.Boolean)
    dateuploaded = db.Column(db.DateTime)
    album_id = db.Column(db.Integer, db.ForeignKey('Album.id'), nullable=False)

    def __init__(self, name, album_id, orig_name, audio_url, interactive):
        self.name = name
        self.album_id = album_id
        self.audio_url = audio_url
        self.orig_name = orig_name
        self.interactive = interactive
        self.dateuploaded = datetime.utcnow()

    def __repr__(self):
        return '<Episode %r>' % self.id

class Interactive_content (db.Model):
    __tablename__ = "Interactive_content"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    content_name = db.Column(db.String)
    orig_name = db.Column(db.String)
    user = db.Column(db.String)
    profile = db.Column(db.String)
    dateuploaded = db.Column(db.DateTime)
    episode_id = db.Column(db.Integer, db.ForeignKey('Episode.id'), nullable=False)

    def __init__(self, episode_id, name, original_name, user, profile, content_name):
        self.name = name
        self.content_name = content_name
        self.episode_id = episode_id
        self.user = user
        self.orig_name = original_name
        self.profile = profile
        self.dateuploaded = datetime.utcnow()

    def __repr__(self):
        return '<Interactive_content %r>' % self.id

class Episode_script (db.Model):
    __tablename__ = "Episode_script"
    id = db.Column(db.Integer, primary_key = True)
    data = db.Column(db.String)
    user = db.Column(db.String)
    profile = db.Column(db.String)
    lastupdated = db.Column(db.DateTime)
    dateuploaded = db.Column(db.DateTime)
    episode_id = db.Column(db.Integer, db.ForeignKey('Episode.id'), nullable=False)

    def __init__(self, user, episode_id, data, profile):
        self.user = user
        self.episode_id = episode_id
        self.data = data
        self.profile = profile
        self.lastupdated = datetime.utcnow()
        self.dateuploaded = datetime.utcnow()

    def __repr__(self):
        return '<Episode_script %r>' % self.id


class Timetable (db.Model):
    __tablename__ = "Timetable"
    id = db.Column(db.Integer, primary_key = True)
