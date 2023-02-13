"""Methods to execute API calls."""

import sgex
from dash import get_app
from flask_caching import Cache

import environment.settings as env
from builtin.call import assemble, parse

app = get_app()
cache = Cache(app.server, config=env.cache_config)


@cache.memoize()
def get_info(data):
    # get text basic corpus info
    params = sgex.parse("builtin/call/corp_info.yml")
    params["id"]["call"] |= {"corpname": data["corpus"]}
    params["id"]["meta"] = data["corpus"]
    sgex.Call(params, server=env.NOSKE_SERVER_NAME, loglevel="warning")
    info = parse.Corp_Info(data["corpus"])
    info.df["size"] = info.df["size"].apply(lambda x: f"{x:,}")
    # get text type analysis
    wlattrs = info.df["structure"] + "." + info.df["name"]
    for wlattr in wlattrs:
        params = sgex.parse("builtin/call/ttype_analysis.yml")
        params["id"]["call"] |= {"corpname": info.meta, "wlattr": wlattr}
        params["id"]["meta"] = f"ttype_analysis {info.meta}"
        sgex.Call(params, server=env.NOSKE_SERVER_NAME, loglevel="warning")
    return info


@cache.memoize()
def make_corpus_attr_options(corpus):
    params = sgex.parse("builtin/call/corp_info.yml")
    params["id"]["call"] |= {"corpname": corpus}
    params["id"]["meta"] = corpus
    sgex.Call(params, server=env.NOSKE_SERVER_NAME, loglevel="warning")
    info = parse.Corp_Info(corpus)
    info.df["attributes"] = info.df["structure"] + "." + info.df["name"]
    info.df.sort_values(["attributes"], inplace=True)
    return [{"label": x, "value": x} for x in info.df["attributes"].values]


@cache.memoize()
def make_calls(corpora, attribute, input_text):
    queries = [x.strip() for x in input_text.split(";")]
    calls = {}
    for corpus in corpora:
        if attribute in env.comparable_attributes:
            fcrit_attr = env.corpora[corpus][attribute]
        else:
            fcrit_attr = attribute
        for query in queries:
            calls[f"{corpus} {query}"] = assemble.freqs_simple(
                query, corpus, fcrit_attr
            )
    sgex.Call(calls, server=env.NOSKE_SERVER_NAME, loglevel="warning")
    params_list = [v["call"] for v in calls.values()]
    return parse.hash_calls(params_list)
