__author__ = 'marcusfaust'
from app import db


class RefreshToken(db.Model):
    __tablename__ = 'refreshtoken'

    refreshtoken = db.Column(db.String())

    def __init__(self, refreshtoken):
        self.refreshtoken = refreshtoken


    def __repr__(self):
        return '<token {}>'.format(self.refreshtoken)