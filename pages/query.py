# Copyright (c) 2023 Loryn Isaacs
# This file is part of Quartz, licensed under GPL3+ https://github.com/engisalor/quartz
import json
import logging
import urllib
from collections import Counter
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, State, ctx, dcc, get_app, html
from flask import request
from sgex.job import Job
from sgex.query import simple_query

from components.aio import aio
from pages import freqs_viz
from settings import corp_data, env, stats
from utils import convert, redirect

app = get_app()

page_name = Path(__file__).stem
title = "Query"
_path = "/"
dash.register_page(__name__, path=_path, title=title)


def layout(
    query="", corpora="", statistics="", attribute="", attribute_filter="", **args
):
    corpora = redirect.corpora(corpora)
    statistics = redirect.statistics(statistics)
    attribute = redirect.attribute(attribute)
    attribute_filter = redirect.attribute_filter(attribute_filter)

    query_box = dbc.InputGroup(
        [
            dbc.Button(
                "Search",
                id="query-button",
                color="light",
                title="Click or press enter to search",
            ),
            dbc.Input(
                value=query,
                id="query-input",
                placeholder="Enter a word or phrase",
                style={"minWidth": "180px", "flexGrow": 2},
            ),
        ],
    )

    corpora_box = html.Div(
        [
            aio.PopoverHeaderAIO("Corpora", title="Select which corpus/corpora to use"),
            dcc.Checklist(
                options=[
                    {"label": v["name"], "value": k} for k, v in corp_data.dt.items()
                ],
                value=corpora,
                id="corpora-picker",
                className="settings-options",
            ),
        ]
    )

    stats_box = html.Div(
        [
            aio.PopoverHeaderAIO(
                "Statistics",
                title="Choose which statistics to display",
            ),
            dcc.Checklist(
                options=[{"label": v, "value": k} for k, v in stats.items()],
                value=statistics,
                id="statistic-picker",
                className="settings-options",
            ),
        ]
    )

    attribute_box = html.Div(
        [
            aio.PopoverHeaderAIO(
                "Attributes",
                title="Select an attribute to study.",
            ),
            dcc.RadioItems(
                value=attribute, id="attribute-picker", className="settings-options"
            ),
        ]
    )

    filter_box = html.Div(
        [
            aio.PopoverHeaderAIO(
                "Attributes filter",
                title="Filter attribute values",
            ),
            html.I(
                id="attribute-filter-all",
                title="Select all",
                className="bi bi-plus-circle",
            ),
            html.I(
                id="attribute-filter-none",
                title="Select none",
                className="bi bi-dash-circle",
            ),
            dcc.Dropdown(
                id="attribute-filter",
                multi=True,
                clearable=False,
                value=attribute_filter,
                placeholder="Filter attribute values",
            ),
        ]
    )

    top_panel = html.Div(
        [
            query_box,
            dbc.Button(
                "Settings",
                id="settings-button",
                color="light",
                title="Show/hide settings",
            ),
            html.I(
                id="table-button",
                title="Show/hide table",
                className="bi bi-table",
            ),
            html.I(
                id="download-frequencies-button",
                title="Download CSV data",
                className="bi bi-download",
            ),
            dcc.Download(id="download-frequencies"),
            dcc.Clipboard(title="Copy URL to current plot", id="url-clipboard"),
            html.I(
                id="guide-button",
                className="bi bi-question-lg",
                title="Show/hide user guide",
            ),
            dbc.Popover(
                dbc.PopoverBody(aio.MarkdownFileAIO(getattr(env, "GUIDE_MD", None))),
                target="guide-button",
                trigger="click",
                style={"overflow": "scroll"},
                placement="bottom",
            ),
            dbc.Popover(
                id="settings-box",
                target="settings-button",
                placement="bottom",
                trigger="click",
                children=[
                    dbc.PopoverBody(
                        [
                            corpora_box,
                            stats_box,
                            attribute_box,
                            filter_box,
                        ]
                    )
                ],
            ),
        ],
        className="top-panel",
    )

    return html.Div(
        [
            dcc.Store(id="store-frequencies", storage_type="session"),
            html.H2(title),
            top_panel,
            dbc.Collapse(
                html.Div(id="table"),
                id="table-collapse",
                is_open=False,
            ),
            html.Br(),
            dcc.Loading(
                id="loading",
                children=[html.Div([html.Div(id="frequencies-content")])],
                type="circle",
            ),
        ]
    )


def set_attribute_value(options, value):
    """Ensures attribute-picker value is valid or falls back to default."""

    if value in [o["value"] for o in options]:
        return value
    else:
        if len(options):
            value = options[0]["value"]
        else:
            value = None
        return value


@dash.callback(
    Output("attribute-picker", "options"),
    Output("attribute-picker", "value"),
    Input("corpora-picker", "value"),
    Input("attribute-picker", "value"),
    State("attribute-picker", "options"),
)
def update_attribute_radio(corpora, value, options):
    """Controls available attributes based on selected corpora."""
    if corpora:
        q = "corpus in @corpora and exclude==False"
        if len(corpora) > 1:
            q += " and comparable==True"
        vals = corp_data.structures.query(q)
        counts = Counter(vals["label"].to_list())
        options = vals.apply(
            lambda row: {"label": row["label"], "value": row["label"]}, axis=1
        ).to_list()
        options = [x for x in options if counts[x["label"]] == len(corpora)]
        options = list({v["label"]: v for v in options}.values())
        options = sorted(options, key=lambda dt: dt["label"])
    else:
        options, value = [], None
    value = set_attribute_value(options, value)
    logging.debug(f"V={value} len(O)={len(options)}")
    return options, value


@dash.callback(
    Output("attribute-filter", "options"),
    Output("attribute-filter", "value"),
    Input("corpora-picker", "value"),
    Input("attribute-picker", "value"),
    Input("attribute-filter-all", "n_clicks"),
    Input("attribute-filter-none", "n_clicks"),
    State("attribute-filter", "options"),
    State("attribute-filter", "value"),
)
def update_attribute_filter(corpora, attribute, all, none, options, value):
    """Controls attribute filters for selected corpora.

    TODO:
        Currently assumes `|` is the multisep for all corpora
        and that all attributes are multivalues. Can cause unwanted
        results if `|` appears in single values. To fix, must parse
        each corpus's config file and adapt behavior to each
        (may not be possible for some third party corpora).
    """

    if not attribute or not corpora:
        logging.debug("empty")
        return [], []
    else:
        df = corp_data.structures
        attrs = df.loc[  # noqa: F841
            (df["corpus"].isin(corpora)) & (df["label"] == attribute), "attr"
        ].to_list()
        vals = corp_data.ttypes.query("corpus in @corpora and attribute in @attrs")
        options = convert.multivalue_to_unique(vals["str"].to_list())
        # reset when incompatible
        if value and options:
            if len([x for x in value if x not in options]):
                value = []
        # toggle all/none values
        if ctx.triggered_id == "attribute-filter-none":
            value = []
        if ctx.triggered_id == "attribute-filter-all":
            value = options
        logging.debug(f"V={value} len(O)={len(options)}")
        return options, value


@dash.callback(
    Output("table-collapse", "is_open"),
    Input("table-button", "n_clicks"),
    State("table-collapse", "is_open"),
    prevent_initial_call=True,
)
def toggle_table_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@dash.callback(
    Output("frequencies-content", "children"),
    Output("table", "children"),
    Input("corpora-picker", "value"),
    Input("attribute-picker", "value"),
    Input("attribute-filter", "value"),
    Input("statistic-picker", "value"),
    Input("store-frequencies", "data"),
    State("query-input", "value"),
    prevent_initial_call=True,
)
def draw(corpora, attribute, attribute_filter, statistics, data, input_text):
    """Draws page content based on options."""
    df = pd.DataFrame.from_dict(data)
    if not len(statistics) or df.empty:
        return html.Div(), html.Div()
    query_args = []
    slice = pd.DataFrame()
    graphs = []
    table = []
    attrs = []
    # filtering
    if len(corpora):
        query_args.append("corpname in @corpora")
    _df = corp_data.structures
    attrs = _df.loc[  # noqa: F841
        (_df["corpus"].isin(corpora)) & (_df["label"] == attribute), "attr"
    ].to_list()
    query_args.append("attribute in @attrs")
    if len(attribute_filter):
        query_args.append("value in @attribute_filter")
    if len(query_args):
        slice = df.query(" and ".join(query_args)).copy()
    else:
        slice = df.copy()
    # melting statistics
    melted_slice = slice.melt(
        id_vars=[x for x in slice.columns if x not in stats.keys()],
        var_name="statistic",
        value_name="f",
    )
    melted_slice.query("statistic in @statistics", inplace=True)
    melted_slice.sort_values("value", inplace=True)
    niceargs = slice["nicearg"].unique().tolist()
    queries = [x.strip() for x in input_text.split(";") if x.strip()]
    args = queries[: env.MAX_QUERIES]
    if len(niceargs) != len(args):
        logging.error(f"len(niceargs) {len(niceargs)} != len(args) {len(args)}")
        return html.Div(), html.Div()
    if not melted_slice.empty:
        arg_map = [[args[x], niceargs[x]] for x in range(len(args))]
        is_choropleth = [corp_data.dt[c].get("choropleth", []) for c in corpora]
        table = freqs_viz.data_table(df, arg_map)
        if attribute in [y for x in is_choropleth for y in x]:
            graphs = freqs_viz.choropleth(melted_slice, arg_map)
        else:
            graphs = freqs_viz.bar_chart(melted_slice, arg_map)

    return graphs, table


@dash.callback(
    Output("store-frequencies", "data"),
    Input("query-input", "n_submit"),
    Input("query-button", "n_clicks"),
    Input("corpora-picker", "value"),
    Input("attribute-picker", "value"),
    State("query-input", "value"),
    prevent_initial_call=True,
)
def send_requests(n_submit, n_clicks, corpora, attribute, input_text):
    if isinstance(input_text, str):
        input_text = input_text.strip()
    if not input_text:
        return {}
    if not len(corpora):
        return {}
    if not attribute:
        return {}

    queries = [x.strip() for x in input_text.split(";") if x.strip()]
    queries = queries[: env.MAX_QUERIES]
    calls = []
    for corpus in corpora:
        label_map = {v: k for k, v in corp_data.dt[corpus]["label"].items()}
        attr = label_map[attribute]
        for query in queries:
            query = query.strip()
            if query.startswith("q,") and len(query) > 2:
                query = "aword," + query[2:]
            else:
                query = "aword," + simple_query(query)
            calls.append(
                {
                    "call_type": "Freqs",
                    "q": query,
                    "corpname": corpus,
                    "fcrit": f"{attr} 0",
                    "freq_sort": "freq",
                    "fmaxitems": env.MAX_ITEMS,
                    "fpage": 1,
                    "group": 0,
                    "showpoc": 1,
                    "showreltt": 1,
                    "showrel": 1,
                }
            )
    j = Job(params=calls, **env.sgex)
    j.run()
    dfs = []
    for call in j.data.freqs:
        df = call.df_from_json()
        df["params"] = json.dumps(call.params)
        dfs.append(df)
    return pd.concat(dfs).to_dict("records")


@dash.callback(
    Output("url-clipboard", "content"),
    Input("url-clipboard", "n_clicks"),
    State("corpora-picker", "value"),
    State("attribute-picker", "value"),
    State("attribute-filter", "value"),
    State("statistic-picker", "value"),
    State("query-input", "value"),
    prevent_initial_call=True,
)
def copy_url(n_clicks, corpora, attribute, attribute_filter, statistics, input_text):
    """Generates URL parameters based on current options."""

    if input_text and corpora and attribute and statistics:
        dt = {
            "query": input_text,
            "corpora": ";".join(corpora),
            "statistics": ";".join(statistics),
            "attribute": attribute,
            "attribute_filter": ";".join(attribute_filter),
        }

        url = (
            request.host_url.rstrip("/")
            + _path.strip("/")
            + "?"
            + urllib.parse.urlencode(dt)
        )
        logging.debug(url)
        return url


@dash.callback(
    Output("download-frequencies", "data"),
    Input("download-frequencies-button", "n_clicks"),
    State("corpora-picker", "value"),
    State("attribute-picker", "value"),
    State("query-input", "value"),
    State("store-frequencies", "data"),
    prevent_initial_call=True,
)
def download_frequencies(n_clicks, corpora, attribute, query, data):
    """Prepares a file of the current data sample to download."""
    if data:
        df = pd.DataFrame.from_dict(data)
        df["corpname"].replace(
            {k: corp_data.dt[k]["name"] for k in corp_data.dt.keys()}, inplace=True
        )
        df.drop(["params"], axis=1, inplace=True)
        df.reset_index(drop=True, inplace=True)
        file = "~".join(["~".join(df["corpname"].unique()), query, attribute])
        logging.debug(file)
        return dcc.send_data_frame(df.to_csv, file + ".csv")
