import logging
import os
from dataclasses import dataclass
from os.path import dirname, join
from pathlib import Path

import pandas as pd
from dotenv import dotenv_values
from sgex.job import Job
from sgex.util import read_yaml

from builtin.utils.io import load_yaml

# logging
logging.basicConfig(
    format="%(levelname)s - %(module)s.%(funcName)s - %(message)s", level=logging.INFO
)


# classes
@dataclass
class ENV:
    """Dataclass with environment variables."""

    def __init__(self):
        dotenv_path = join(dirname(__file__), os.getenv("ENVIRONMENT_FILE"))
        dt = dotenv_values(dotenv_path) | {
            k: v for k, v in os.environ.items() if k.startswith("SGEX_")
        }
        for k, v in dt.items():
            if v.lower() == "true":
                v = True
            elif v.lower() == "false":
                v = False
            elif k == "ACTIVE_DIR":
                v = Path(v)
            elif k == "MAX_QUERIES":
                v = int(v)
            setattr(self, k, v)


@dataclass
class CorpData:
    """Dataclass with corpus data."""

    def __init__(self):
        # load corpora file
        self.dt = read_yaml(env.ACTIVE_DIR / Path("config/corpora.yml"))
        corp_ids = list(self.dt.keys())
        # make corpinfo calls
        corpinfo_calls = [
            {"call_type": "CorpInfo", "corpname": x, "struct_attr_stats": 1}
            for x in corp_ids
        ]
        j = Job(verbose=True, thread=True, params=corpinfo_calls)
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
        j = Job(verbose=True, thread=True, params=wordlist_calls)
        j.run()
        self.ttypes = pd.DataFrame()
        for call in j.data.wordlist:
            _ttypes = call.df_from_json()
            _ttypes["corpus"] = call.params["corpname"]
            self.ttypes = pd.concat([self.ttypes, _ttypes])


env = ENV()
corp_data = CorpData()
stats = {
    "reltt": "relative text type fpm",
    "frq": "occurrences",
    "rel": "relative density %",
    "fpm": "frequency per million",
}
labels_file = env.ACTIVE_DIR / Path("config/labels.yml")
if labels_file.exists():
    labels = load_yaml(labels_file)
else:
    labels = {}
