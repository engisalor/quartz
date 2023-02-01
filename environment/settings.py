# settings.py
import os
from os.path import dirname, join

from dotenv import load_dotenv

from builtin.utils import io

dotenv_path = join(dirname(__file__), os.getenv("ENVIRONMENT_FILE"))
load_dotenv(dotenv_path=dotenv_path, override=True)

# dash settings
HOST = os.environ.get("HOST")
PORT = int(os.environ.get("PORT"))
DASH_DEBUG = bool(os.environ.get("DASH_DEBUG"))

# cache settings
if os.environ.get("CACHE_REDIS_HOST"):
    cache_config = {
        "CACHE_TYPE": "RedisCache",
        "CACHE_DEFAULT_TIMEOUT": int(os.environ.get("CACHE_DEFAULT_TIMEOUT")),
        "CACHE_REDIS_HOST": os.environ.get("CACHE_REDIS_HOST"),
        "CACHE_REDIS_PASSWORD": os.environ.get("CACHE_REDIS_PASSWORD"),
        "CACHE_REDIS_PORT": int(os.environ.get("CACHE_REDIS_PORT")),
    }
else:
    cache_config = {
        "CACHE_TYPE": "FileSystemCache",
        "CACHE_DEFAULT_TIMEOUT": int(os.environ.get("CACHE_DEFAULT_TIMEOUT")),
        "CACHE_DIR": os.environ.get("CACHE_DIR"),
        "CACHE_THRESHOLD": int(os.environ.get("CACHE_THRESHOLD")),
    }

# default locations
NOSKE_SERVER_NAME = os.environ.get("NOSKE_SERVER_NAME")
ASSETS_DIR = os.environ.get("ASSETS_DIR")
PAGES_DIR = os.environ.get("PAGES_DIR")
LAYOUT_MODULE = os.environ.get("LAYOUT_MODULE")
CORPORA_FILE = os.environ.get("CORPORA_FILE")

# corpora
if CORPORA_FILE:
    corpora = io.load_yaml(CORPORA_FILE)
else:
    corpora = None
