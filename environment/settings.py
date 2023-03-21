import collections
import logging
import os
from os.path import dirname, join

import pandas as pd
import sgex
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from requests_cache import SerializerPipeline, Stage, pickle_serializer

from builtin.utils import io

# logging
logging.basicConfig(
    format="%(levelname)s - %(module)s.%(funcName)s - %(message)s", level=logging.INFO
)

# environment
dotenv_path = join(dirname(__file__), os.getenv("ENVIRONMENT_FILE"))
load_dotenv(dotenv_path=dotenv_path, override=True)
# env variables
HOST = os.environ["HOST"]
PORT = int(os.environ["PORT"])
DASH_DEBUG = bool(os.environ["DASH_DEBUG"])
REDIRECT_POLICY = os.environ["REDIRECT_POLICY"]
SGEX_SERVER = os.environ["SGEX_SERVER"]
SGEX_CONFIG = sgex.config.load("SGEX_CONFIG_JSON")
SERIALIZER_KEY = Fernet(os.environ["SERIALIZER_KEY"])
ASSETS_DIR = os.environ["ASSETS_DIR"]
PAGES_DIR = os.environ["PAGES_DIR"]
LAYOUT_MODULE = os.environ["LAYOUT_MODULE"]
CORPORA_FILE = os.environ["CORPORA_FILE"]


# functions
# fix issue with sgex 0.6.2 parsing behavior (for corpora w/ labeled attributes)
# TODO remove when addressed upstream
def clean_heads(heads) -> list:
    """Extracts each block's fcrit attribute: ``head[0]["id"]``."""
    if len([x for x in heads if x]):
        return [head[0].get("id") for head in heads]
    else:
        return None


sgex.parse.freqs.clean_heads = clean_heads


# for running corpus text type analysis (needed for initial configuration)
def premake_calls(corpus, SGEX_SERVER, SGEX_CONFIG, session_params):
    # corp_info call
    p = sgex.Package(
        sgex.CorpInfo({"corpname": corpus, "struct_attr_stats": 1}),
        SGEX_SERVER,
        SGEX_CONFIG,
        session_params=session_params,
    )
    logging.debug(f"CORP_INFO {corpus}")
    p.send_requests()
    structures_df = sgex.parse.corp_info.structures_json(p.responses[0])
    sizes_df = sgex.parse.corp_info.sizes_json(p.responses[0])
    # attributes list
    attributes = structures_df["structure"] + "." + structures_df["attribute"]
    # text type calls
    wordlist_params = {
        "corpname": corpus,
        "wlattr": None,
        "wlmaxitems": 50,
        "wlsort": "frq",
        "wlpat": ".*",
        "wlminfreq": 1,
        "wlicase": 1,
        "wlmaxfreq": 0,
        "wltype": "simple",
        "include_nonwords": 1,
        "random": 0,
        "relfreq": 1,
        "reldocf": 0,
        "wlpage": 1,
    }
    ttype_calls = []
    for attr in attributes:
        params = {**wordlist_params, "wlattr": attr}
        ttype_calls.append(sgex.Wordlist(params))
    ttype_package = sgex.Package(
        ttype_calls, SGEX_SERVER, SGEX_CONFIG, session_params=session_params
    )
    logging.debug(f"TTYPES {corpus}")
    ttype_package.send_requests()
    # most common text types
    dfs = [sgex.parse.wordlist.ttype_analysis_json(r) for r in ttype_package.responses]
    ttypes_df = pd.concat(dfs)
    return {
        "sizes_df": sizes_df,
        "structures_df": structures_df,
        "attributes_ls": attributes,
        "ttypes_df": ttypes_df,
    }


# corpora settings
corpora = io.load_yaml(CORPORA_FILE)
dicts = [corpora.get(k).get("comparable_attributes", {}) for k in corpora.keys()]
attrs = [y for x in dicts for y in x.keys()]
comparable_attributes = [i for i, c in collections.Counter(attrs).items() if c > 1]


# SGEX settings
# to make a key (supply securely afterward)
# Fernet.generate_key().decode()
# define the serializer
serializer = SerializerPipeline(
    [
        pickle_serializer,
        Stage(dumps=SERIALIZER_KEY.encrypt, loads=SERIALIZER_KEY.decrypt),
    ],
    is_binary=True,
)
# parameters for the `requests-cache` session
session_params = dict(
    cache_name="data/requests_cache",
    serializer=serializer,
    backend="filesystem",
    ignored_parameters=sgex.config.credential_parameters,
    key_fn=sgex.call.call.create_custom_key,
    allowable_codes=[200, 400],
)
# get initial calls
premade_calls = {
    corpus: premake_calls(corpus, SGEX_SERVER, SGEX_CONFIG, session_params)
    for corpus in list(corpora.keys())
}


# graph labels
statistics = {
    "frq": "occurrences",
    "rel": "relative density %",
    "fpm": "frequency per million",
    "reltt": "relative text type fpm",
}

labels = io.load_yaml("environment/labels.yml")
if labels:
    labels |= statistics
else:
    labels = statistics
