import json
import pandas as pd
import sqlite3 as sql

from builtin.utils.convert import list_of_dict


def get_responses(id: str, db: str):
    """Gets response data from a database matching ``id`` and parse JSON strings.
    
    TODO:
        - generalize, decide on whether/how to use "id" field"""

    conn = sql.Connection(db)
    c = conn.cursor()
    res = c.execute(
        """SELECT response FROM calls 
        WHERE id = ? AND error IS null""",
        (id,))
    responses = res.fetchall()
    return [json.loads(x[0]) for x in responses]


def clean_items(items, item_keys=["Word", "frq", "rel", "fpm"]):
    """Extracts desired items from block and flattens ``Word`` values."""

    clean = []
    for block in items:
        b = []
        for i in block:
            dt = {k:v for k,v in i.items() if k in item_keys}
            words = list_of_dict(dt["Word"])
            dt["value"] = "|".join(words["n"])
            del dt["Word"]
            b.append(dt)
        clean.append(b)
    return clean


def clean_heads(heads):
    """Extracts each block's fcrit attribute: ``head[0]["n"]``."""

    return [head[0].get("n") for head in heads]


def response_to_df(response: dict):
    """Converts a response with JSON data to a DataFrame.
    
    Note:
        Tested with single- and multi-block ``freqs`` calls.
    """

    # extract data from response
    blocks = response.get("Blocks", [])
    heads = clean_heads([block["Head"] for block in blocks])
    items = clean_items([block["Items"] for block in blocks])
    # combine extracted data
    for b in range(len(blocks)):
        for i in range(len(items[b])):
            items[b][i]["attribute"] = heads[b]
    # convert to DataFrame
    df = pd.DataFrame.from_records([x for y in items for x in y])
    # get specific values
    df["arg"] = response.get("Desc",[])[0].get("arg",{})
    df["nicearg"] = response.get("Desc",[])[0].get("nicearg",{})
    df["corpname"] = response.get("request", {}).get("corpname",{})
    return df


class Parse_Responses:
    """Reads SkE API response JSON data from DB and converts to a DataFrame."""

    def __init__(self, id, db="data/sgex.db") -> pd.DataFrame:
        responses = get_responses(id, db)

        # combine responses
        df = pd.DataFrame()
        for response in responses:
            df = pd.concat([df, response_to_df(response)])
        # clean final df
        df = df.round(2)
        df.sort_values("value",inplace=True)
        # set attributes
        self.id = id
        self.db = db
        self.df = df
