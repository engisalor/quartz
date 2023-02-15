import collections
import logging
import os
from os.path import dirname, join

from dotenv import load_dotenv

from builtin.utils import io

dotenv_path = join(dirname(__file__), os.getenv("ENVIRONMENT_FILE"))
load_dotenv(dotenv_path=dotenv_path, override=True)

# logging
logging.basicConfig(
    format="%(levelname)s - %(module)s.%(funcName)s - %(message)s", level=logging.DEBUG
)

# dash settings
HOST = os.environ.get("HOST")
PORT = int(os.environ.get("PORT"))
DASH_DEBUG = bool(os.environ.get("DASH_DEBUG"))
REDIRECT_POLICY = os.environ.get("REDIRECT_POLICY")

# cache settings
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

# corpora settings
if CORPORA_FILE:
    corpora = io.load_yaml(CORPORA_FILE)
    dicts = [corpora.get(k).get("comparable_attributes", {}) for k in corpora.keys()]
    attrs = [y for x in dicts for y in x.keys()]
    comparable_attributes = [i for i, c in collections.Counter(attrs).items() if c > 1]
else:
    corpora = None
    comparable_attributes = None

# graph labels
statistics = {
    "frq": "occurrences",
    "rel": "relative density %",
    "fpm": "frequency per million",
    "reltt": "relative fpm",
}

labels = {
    "nicearg": "query",
    "corpname": "corpus",
} | statistics
