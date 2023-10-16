import logging
import os
from dataclasses import dataclass

import pandas as pd
from sgex.job import Job
from sgex.util import read_yaml

# logging
logging.basicConfig(
    format="%(levelname)s - %(module)s.%(funcName)s - %(message)s", level=logging.INFO
)


# classes
@dataclass
class ENV:
    """Dataclass with environment variables."""

    def __init__(self):
        self.HOST = os.getenv("HOST")
        self.PORT = os.getenv("PORT")
        self.REDIRECT_POLICY = os.getenv("REDIRECT_POLICY")
        self.CORPORA_YML = os.getenv("CORPORA_YML")
        self.CORPORA_MD = os.getenv("CORPORA_MD")
        self.GUIDE_MD = os.getenv("GUIDE_MD")
        self.HOME_MD = os.getenv("HOME_MD")
        self.MAX_QUERIES = os.getenv("MAX_QUERIES")
        self.MAX_ITEMS = os.getenv("MAX_ITEMS")
        self.DASH_DEBUG = os.getenv("DASH_DEBUG").lower()
        for k, v in self.__dict__.items():
            if (
                v.startswith("'")
                and v.endswith("'")
                or v.startswith('"')
                and v.endswith('"')
            ):
                setattr(self, k, v.strip("\"'"))
            if k in ["MAX_QUERIES", "MAX_ITEMS"]:
                setattr(self, k, int(v))
            if k in ["DASH_DEBUG"]:
                setattr(self, k, v.lower() == "true")
        self.sgex = {
            "api_key": os.getenv("SGEX_API_KEY"),
            "server": os.getenv("SGEX_SERVER"),
            "thread": os.getenv("SGEX_THREAD"),
            "username": os.getenv("SGEX_USERNAME"),
            "verbose": os.getenv("SGEX_VERBOSE"),
            "wait_dict": os.getenv("SGEX_WAIT_DICT"),
        }
        for k, v in self.sgex.items():
            if not v:
                pass
            elif (
                v.startswith("'")
                and v.endswith("'")
                or v.startswith('"')
                and v.endswith('"')
            ):
                self.sgex[k] = v.strip("\"'")
            if k in ["verbose", "thread"] and isinstance(v, str):
                self.sgex[k] = v.lower() == "true"
        self.sgex = {k: v for k, v in self.sgex.items() if v}


@dataclass
class CorpData:
    """Dataclass with corpus data."""

    def __init__(self):
        # load corpora file
        self.dt = read_yaml(env.CORPORA_YML)
        corp_ids = list(self.dt.keys())
        # make corpinfo calls
        corpinfo_calls = [
            {"call_type": "CorpInfo", "corpname": x, "struct_attr_stats": 1}
            for x in corp_ids
        ]
        j = Job(params=corpinfo_calls, **env.sgex)
        j.run()
        # make wordlist calls (text type data)
        wordlist_params = {
            "call_type": "Wordlist",
            "wlattr": None,
            "wlmaxitems": env.MAX_ITEMS,
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
        wordlist_calls = []
        self.structures = pd.DataFrame()
        self.sizes = pd.DataFrame()

        def get_label(row: dict) -> str | None:
            return self.dt.get(row["corpus"]).get("label").get(row["attr"], row["attr"])

        def is_in_list(row: dict, key: str) -> bool:
            return row["attr"] in self.dt.get(row["corpus"]).get(key, [])

        for x in range(len(corp_ids)):
            _structures = j.data.corpinfo[x].structures_from_json()
            _structures["corpus"] = corp_ids[x]
            _structures["attr"] = (
                _structures["structure"] + "." + _structures["attribute"]
            )
            _structures["comparable"] = _structures.apply(
                is_in_list, key="comparable", axis=1
            )
            _structures["label"] = _structures.apply(get_label, axis=1)
            _structures["exclude"] = _structures.apply(
                is_in_list, key="exclude", axis=1
            )
            _structures["choropleth"] = _structures.apply(
                is_in_list, key="choropleth", axis=1
            )
            self.structures = pd.concat([self.structures, _structures])
            _sizes = j.data.corpinfo[x].sizes_from_json()
            _sizes["corpus"] = corp_ids[x]
            self.sizes = pd.concat([self.sizes, _sizes])
            wordlist_calls.extend(
                [
                    {**wordlist_params, "wlattr": attr, "corpname": corp_ids[x]}
                    for attr in _structures["attr"]
                ]
            )
        j = Job(params=wordlist_calls, **env.sgex)
        j.run()
        self.ttypes = pd.DataFrame()
        for call in j.data.wordlist:
            _ttypes = call.df_from_json()
            _ttypes["corpus"] = call.params["corpname"]
            self.ttypes = pd.concat([self.ttypes, _ttypes])


env = ENV()
corp_data = CorpData()
stats = {
    "reltt": "reltt - relative text type fpm",
    "frq": "frq - occurrences",
    "rel": "rel - relative density %",
    "fpm": "fpm - frequency per million",
}
