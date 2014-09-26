__author__ = 'marcusfaust'

import os
from flask.ext.sqlalchemy import SQLAlchemy
from Crypto.Cipher import ARC4

db = SQLAlchemy()

class RefreshToken(db.Model):
    __tablename__ = 'rtokens'

    id = db.Column(db.Integer(), primary_key=True)
    token = db.Column(db.String())

    def __repr__(self):
        return '<token {}>'.format(self.token)

class RunLog(db.Model):
    __tablename__ = 'runlog'

    id = db.Column(db.Integer(), primary_key=True)
    datetime = db.Column(db.DateTime())
    nars_found = db.Column(db.Boolean())
    duration = db.Column(db.Float())

    def __init__(self, datetime, nars_found, duration):
        self.datetime = datetime
        self.nars_found = nars_found
        self.duration = duration

    def __repr__(self):
        return '<id {}>'.format(self.id)


class User(db.Model):
    __tablename__ = 'user'

    __ARC4_KEY__ = os.environ.get('ARC4_KEY')
    arc4 = ARC4.new(__ARC4_KEY__)

    id = db.Column(db.Integer(), primary_key=True)
    boxuser = db.Column(db.String(), unique=True)
    mitrend_user = db.Column(db.String())
    is_enabled = db.Column(db.Boolean())
    password_ciphertext = db.Column(db.Binary())
    incoming_folder_id = db.Column(db.String())
    archive_folder_id = db.Column(db.String())

    def __init__(self, boxuser, mitrend_user, is_enabled, password_cleartext):
        self.boxuser = boxuser
        self.mitrend_user = mitrend_user
        self.is_enabled = is_enabled
        self.password_ciphertext = self.encrypt_password(password_cleartext)

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def encrypt_password(self, cleartext):
        cipher_text = self.arc4.encrypt(cleartext)
        return cipher_text
