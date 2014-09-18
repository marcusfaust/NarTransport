__author__ = 'marcusfaust'
from app import db


class RefreshToken(db.Model):
    __tablename__ = 'rtokens'

    id = db.Column(db.Integer(), primary_key=True)
    token = db.Column(db.String())

    def __repr__(self):
        return '<token {}>'.format(self.token)