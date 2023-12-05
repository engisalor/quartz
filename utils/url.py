# Copyright (c) 2023 Loryn Isaacs
# This file is part of Quartz, licensed under GPL3+ https://github.com/engisalor/quartz
import json
import re
from urllib import parse

from sgex.query import _query_escape


def split_q(q: str | list) -> tuple:
    """Returns a tuple of (default_attr, cql) from a query (e.g., 'aword,"sun"')."""
    if isinstance(q, list):
        return re.search(r"^a(.*?),(.+)", q[0]).groups()
    else:
        return re.search(r"^a(.*?),(.+)", q).groups()


def split_attr_path(attr_path: str) -> tuple:
    """Returns a tuple of (struct, attr) from an attribute path (e.g., 'doc.file')."""
    return re.search(r"^([\w]+)\.(.+)", attr_path).groups()


def cql(
    params: dict,
    base_url: str,
):
    """Returns a concordance URL based on API call parameters.

    Example base_url:
        `https://app.sketchengine.eu/#concordance?`
    """
    _params = params.copy()
    default_attr, _params["cql"] = split_q(_params["q"])
    del _params["q"]
    template = {
        "tab": "advanced",
        "queryselector": "cql",
        "showresults": "1",
        "default_attr": default_attr,
    }
    query = parse.urlencode(_params | template, quote_via=parse.quote)
    base = parse.urlsplit(base_url, allow_fragments=False)
    return base._replace(query=query).geturl()


def cql_ttype_filter(
    params: dict,
    attr_path: str,
    value: str,
    base_url: str,
) -> str:
    """Returns a concordance URL with a text type filter based on API call params.

    Example base_url:
        `https://app.sketchengine.eu/#concordance?`
    """
    struct, attr = split_attr_path(attr_path)
    _filter = f' [] within <{struct} {attr}="{_query_escape(value)}" />'
    _, cql = split_q(params["q"])
    template = [
        ("corpname", params["corpname"]),
        ("tab", "advanced"),
        ("queryselector", "cql"),
        ("cql", cql),
        ("showresults", "1"),
        (
            "operations",
            json.dumps(
                [
                    {
                        "name": "cql",
                        "arg": cql,
                        "query": {"queryselector": "cqlrow", "cql": cql},
                    },
                    {
                        "name": "filter",
                        "arg": _filter,
                        "query": {
                            "pnfilter": "p",
                            "queryselector": "cqlrow",
                            "inclkwic": True,
                            "filfpos": "0",
                            "filtpos": "0<0",
                            "partial_match": 0,
                            "cql": _filter,
                        },
                    },
                ],
                ensure_ascii=False,
            ),
        ),
    ]
    base = parse.urlsplit(base_url, allow_fragments=False)
    query = parse.urlencode(template, quote_via=parse.quote)
    return base._replace(query=query).geturl()
