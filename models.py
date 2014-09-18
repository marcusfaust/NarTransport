__author__ = 'marcusfaust'
from app import db


class RefreshToken(db.Model):
    __tablename__ = 'rtokens'

    refreshtoken = db.Column(db.String(), primary_key=True)

    def __repr__(self):
        return '<token {}>'.format(self.refreshtoken)