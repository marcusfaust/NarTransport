__author__ = 'marcusfaust'
from app import db


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
    duration = db.Column(db.Integer())

    def __repr__(self):
        return '<id {}>'.format(self.id)