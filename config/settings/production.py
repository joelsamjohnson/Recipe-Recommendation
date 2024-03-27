from .base import *
import django_heroku


DEBUG = False
ALLOWED_HOSTS = ['recipe-backend-api.herokuapp.com']

INSTALLED_APPS += [
    'cloudinary_storage',
    'cloudinary',
]

# Media
MEDIA_URL = '/media/'
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Cloudinary configs
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': config('CLOUDINARY_API_SECRET'),
    'API_SECRET': config('CLOUDINARY_API_KEY')
}

django_heroku.settings(locals())

import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("C:/Users/saraj/PycharmProjects/recipe-api/recipe-recommendation-sy-7facd-firebase-adminsdk-h523u-b428a4ca19.json")
firebase_admin.initialize_app(cred)

