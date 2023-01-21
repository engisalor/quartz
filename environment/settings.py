# settings.py
import os
from os.path import dirname, join

from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), os.getenv("ENVIRONMENT_FILE"))
load_dotenv(dotenv_path=dotenv_path, override=True)

HOST = os.environ.get("HOST")
PORT = int(os.environ.get("PORT"))
DASH_DEBUG = bool(os.environ.get("DASH_DEBUG"))
NOSKE_SERVER_NAME = os.environ.get("NOSKE_SERVER_NAME")
ASSETS_DIR = os.environ.get("ASSETS_DIR")
PAGES_DIR = os.environ.get("PAGES_DIR")
LAYOUT_MODULE = os.environ.get("LAYOUT_MODULE")
