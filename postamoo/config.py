import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEBUG_ENABLED = os.environ['DEBUG_ENABLED'] == '1'

AUTH_PROVIDER_URL = os.environ['AUTH_PROVIDER_URL'].rstrip('/')

DATABASE_URL = os.environ['DATABASE_URL']
TEST_DATABASE_URL = os.environ['TEST_DATABASE_URL']

MEDIA_UPLOAD_FOLDER = os.environ['MEDIA_UPLOAD_FOLDER']
MEDIA_STORAGE_PATH = os.path.join(BASE_DIR, MEDIA_UPLOAD_FOLDER)

MAX_IMAGE_SIZE = int(os.environ['MAX_IMAGE_SIZE'])
MAX_VIDEO_SIZE = int(os.environ['MAX_VIDEO_SIZE'])
