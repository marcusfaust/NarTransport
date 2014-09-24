__author__ = 'marcusfaust'
import os

SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
CSRF_ENABLED = True
SECRET_KEY = 'N0T-T00-s3cr3T'