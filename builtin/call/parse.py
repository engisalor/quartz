import json
import sqlite3 as sql

import pandas as pd

from builtin.utils.convert import list_of_dict


def get_responses(meta, db="data/sgex.db"):
    """Gets response data with matching ``meta`` and parses JSON strings.

    Args:
        meta: string or list of strings to select SQL rows.
        db: SGEX database to select content from."""

    if not isinstance(meta, list):
        meta = [meta]

    v = ",".join(["?"] * len(meta))
    conn = sql.Connection(db)
    c = conn.cursor()
    res = c.execute(
        f"SELECT response FROM calls WHERE meta IN ({v}) AND error IS null",  # nosec
        tuple(meta),
    )
    responses = res.fetchall()
    return [json.loads(x[0]) for x in responses]


class Corp_Info:
    """Class for parsing ``corp_info`` API data."""

    def get_dfs(self):
        df = pd.DataFrame()
        for s in self.json["structures"]:
            temp = pd.DataFrame.from_records(s)
            if not temp.empty:
                temp.drop(["size", "label"], axis=1, inplace=True)
                temp.rename({"name": "structure"}, axis=1, inplace=True)
                temp = pd.concat([temp, pd.json_normalize(temp["attributes"])], axis=1)
                temp.drop(
                    ["attributes", "label", "dynamic", "fromattr"], axis=1, inplace=True
                )
                df = pd.concat([df, temp])
        return df

    def get_sizes(self):
        return pd.DataFrame(
            {
                "structure": [
                    k.replace("count", "") for k in self.json["sizes"].keys()
                ],
                "size": [f"{int(v):,}" for v in self.json["sizes"].values()],
            }
        )

    def __init__(self, meta) -> pd.DataFrame:
        self.meta = meta
        self.json = get_responses(meta)[0]
        self.df = self.get_dfs()
        self.sizes = self.get_sizes()


class Wordlist:
    """Class for parsing ``wordlist`` API data."""

    def __init__(self, meta) -> pd.DataFrame:
        responses = get_responses(meta)

        df = pd.DataFrame()
        for response in responses:
            if response:
                temp = pd.DataFrame.from_records(response["Items"])
                temp["attribute"] = response["request"]["wlattr"]
                df = pd.concat([df, temp])
        if not df.empty:
            df = df.round(2)
            df.sort_values("frq", ascending=False, inplace=True)
        self.meta = meta
        self.df = df


def clean_items(items, item_keys=["Word", "frq", "rel", "fpm"]):
    """Extracts desired items from block and flattens ``Word`` values."""

    clean = []
    for block in items:
        b = []
        for i in block:
            dt = {k: v for k, v in i.items() if k in item_keys}
            words = list_of_dict(dt["Word"])
            dt["value"] = "|".join(words["n"])
            del dt["Word"]
            b.append(dt)
        clean.append(b)
    return clean


def clean_heads(heads):
    """Extracts each block's fcrit attribute: ``head[0]["n"]``."""

    if len([x for x in heads if x]):
        return [head[0].get("n") for head in heads]
    else:
        return None


def response_to_df(response: dict):
    """Converts a response with JSON data to a DataFrame.

    Note:
        Tested with single- and multi-block ``freqs`` calls.
    """

    # extract data from response
    blocks = response.get("Blocks", [])
    heads = clean_heads([block.get("Head") for block in blocks])
    if not heads:
        return pd.DataFrame()
    else:
        items = clean_items([block.get("Items") for block in blocks])
        # combine extracted data
        for b in range(len(blocks)):
            for i in range(len(items[b])):
                items[b][i]["attribute"] = heads[b]
        # convert to DataFrame
        df = pd.DataFrame.from_records([x for y in items for x in y])
        # get specific values
        df["arg"] = response.get("Desc", [])[0].get("arg", {})
        df["nicearg"] = response.get("Desc", [])[0].get("nicearg", {})
        df["corpname"] = response.get("request", {}).get("corpname", {})
        return df


class Freqs:
    """Reads SkE API response JSON data from DB and converts to a DataFrame."""

    def make_df(self):
        responses = get_responses(self.meta, self.db)
        df = pd.DataFrame()
        for response in responses:
            if response:
                df = pd.concat([df, response_to_df(response)])
        if not df.empty:
            df = df.round(2)
            df.sort_values("value", inplace=True)
        return df

    def __init__(self, meta, db="data/sgex.db") -> pd.DataFrame:
        self.meta = meta
        self.db = db
        self.df = self.make_df()
