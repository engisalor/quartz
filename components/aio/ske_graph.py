import json
import re
import uuid
from urllib import parse

import dash_bootstrap_components as dbc
from dash import MATCH, Input, Output, callback, dcc, html

from settings import env


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
    base_url: str = "https://app.sketchengine.eu/#concordance?",
):
    """Returns a URL from given API call parameters."""
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
    base_url: str = "https://app.sketchengine.eu/#concordance?",
) -> str:
    """Returns a URL with a text type filter from given API call params."""
    struct, attr = split_attr_path(attr_path)
    _filter = f" [] within <{struct} {attr}={json.dumps(value,ensure_ascii=False)} />"
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


class SkeGraphAIO(html.Div):
    class ids:
        title_link = lambda aio_id: {  # noqa: E731
            "type": "SkeGraphAIO",
            "group": aio_id,
        }
        graph = lambda aio_id: {  # noqa: E731
            "type": "Graph",
            "group": aio_id,
        }

    ids = ids

    def __init__(
        self,
        title: str,
        aio_id=None,
        **kwargs,
    ):
        if aio_id is None:
            aio_id = str(uuid.uuid4())

        if env.SERVER_URL:
            title_div = html.Div(
                [
                    html.H2(title),
                    dbc.NavLink(
                        html.H3(
                            html.I(className="bi bi-link"),
                            title="Click a data point to get its URL,"
                            + " then click here to open",
                        ),
                        id=self.ids.title_link(aio_id),
                        target="_blank",
                    ),
                ],
                style={
                    "display": "flex",
                    "margin": 0,
                    "justify-content": "space-between",
                },
            )
        else:
            title_div = html.H2(title, style={"margin": 0})

        super().__init__([title_div, dcc.Graph(id=self.ids.graph(aio_id), **kwargs)])

    @callback(
        Output(ids.title_link(MATCH), "href"),
        Input(ids.graph(MATCH), "clickData"),
    )
    def update_link(clickData):
        if clickData and env.SERVER_URL:
            ls = clickData.get("points")[0].get("customdata")
            return cql_ttype_filter(
                params=json.loads(ls[0]),
                attr_path=ls[1],
                value=ls[2],
                base_url=env.SERVER_URL.rstrip("/") + "/#concordance?",
            )
