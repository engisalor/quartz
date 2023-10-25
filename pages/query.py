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
from dash import ALL, Input, Output, State, ctx, dcc, get_app, html
from flask import request
from sgex.job import Job
from sgex.query import simple_query

from components import freqs_batch, freqs_fig
from components.aio import aio
from components.aio.ske_graph import _df_from_crossfilter
from settings import corp_data, env, stats
from utils import convert, redirect

app = get_app()

page_name = Path(__file__).stem
title = "Query"
_path = "/"
dash.register_page(__name__, path=_path, title=title)


def layout(
    query="",
    corpora="",
    statistics="",
    attribute="",
    crossfilter="",
    attribute_filter="",
    **args,
):
    corpora = redirect.corpora(corpora)
    statistics = redirect.statistics(statistics)
    attribute = redirect.attribute(attribute)
    crossfilter = redirect.attribute(crossfilter)
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

    crossfilter_box = html.Div(
        [
            aio.PopoverHeaderAIO(
                "Crossfilter",
                title="Study an attribute within another.",
            ),
            dcc.RadioItems(
                value=crossfilter, id="crossfilter-picker", className="settings-options"
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
                            crossfilter_box,
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
            html.H2(title),
            top_panel,
            dbc.Collapse(
                html.Div(id="table"),
                id="table-collapse",
                is_open=False,
            ),
            html.Br(),
            html.Div(id="frequencies-content", className="frequencies-content"),
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


def set_attribute_options(corpora, value, options, extra=[]):
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
        options = extra + options
    else:
        options, value = [], None
    value = set_attribute_value(options, value)
    return options, value


@dash.callback(
    Output("attribute-picker", "options"),
    Output("attribute-picker", "value"),
    Input("corpora-picker", "value"),
    Input("attribute-picker", "value"),
    State("attribute-picker", "options"),
)
def update_attribute_radio(corpora, value, options):
    """Controls available attributes based on selected corpora."""
    return set_attribute_options(corpora, value, options)


@dash.callback(
    Output("crossfilter-picker", "options"),
    Output("crossfilter-picker", "value"),
    Input("corpora-picker", "value"),
    Input("crossfilter-picker", "value"),
    State("crossfilter-picker", "options"),
)
def update_crossfilter_dropdown(corpora, value, options):
    """Controls available crossfilters based on selected corpora."""
    return set_attribute_options(
        corpora, value, options, extra=[{"label": "no crossfilter", "value": ""}]
    )


@dash.callback(
    Output("attribute-filter", "value"),
    Input("corpora-picker", "value"),
    Input("attribute-picker", "value"),
    Input("attribute-filter-all", "n_clicks"),
    Input("attribute-filter-none", "n_clicks"),
    State("attribute-filter", "options"),
    State("attribute-filter", "value"),
)
def reset_attribute_filter(corpora, attribute, all, none, options, value):
    """Controls attribute filters for selected corpora.

    TODO:
        Currently assumes `|` is the multisep for all corpora
        and that all attributes are multivalues. Can cause unwanted
        results if `|` appears in single values. To fix, must parse
        each corpus's config file and adapt behavior to each
        (may not be possible for some third party corpora).
    """

    if ctx.triggered_id == "attribute-filter-none":
        value = []
    if ctx.triggered_id == "attribute-filter-all":
        value = options
    return value


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


def send_requests(input_text, corpora, attribute):
    queries = [x.strip() for x in input_text.split(";") if x.strip()]
    queries = queries[: env.MAX_QUERIES]
    calls = []
    query_map = {}
    for corpus in corpora:
        label_map = {v: k for k, v in corp_data.dt[corpus]["label"].items()}
        attr = label_map[attribute]
        for query in queries:
            query = query.strip()
            if query.startswith("q,") and len(query) > 2:
                cql = query[2:]
            else:
                cql = simple_query(query)
            query_map |= {cql: query}
            calls.append(
                {
                    "call_type": "Freqs",
                    "q": "aword," + cql,
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
        if not df.empty:
            df["params"] = json.dumps(call.params)
            df["query"] = df["arg"].replace(query_map)
        dfs.append(df)
    return pd.concat(dfs)


@dash.callback(
    Output("frequencies-content", "children"),
    Output("table", "children"),
    Output("attribute-filter", "options"),
    Input("query-input", "n_submit"),
    Input("query-button", "n_clicks"),
    Input("corpora-picker", "value"),
    Input("attribute-picker", "value"),
    Input("attribute-filter", "value"),
    Input("statistic-picker", "value"),
    State("query-input", "value"),
    State("attribute-filter", "options"),
)
def run_query(
    n_submit, n_clicks, corpora, attribute, a_filter, statistics, input_text, a_options
):
    # parse inputs
    if isinstance(input_text, str):
        input_text = input_text.strip()
    if not input_text or not len(corpora) or not attribute or not statistics:
        return html.P("Incomplete settings", className="lead"), None, []
    queries = [x.strip() for x in input_text.split(";") if x.strip()]
    if len(queries) != len(set(queries)):
        return html.P("No duplicate queries", className="lead"), None, []
    if len(queries) > env.MAX_QUERIES:
        return (
            html.P(f"{env.MAX_QUERIES} > queries supported", className="lead"),
            None,
            [],
        )
    # get data
    df = send_requests(input_text, corpora, attribute)
    if df.empty:
        return html.P("Nothing found", className="lead"), None, []
    # manage filter
    a_options = df["value"].to_list()
    if [x for x in a_options if "|" in x]:
        logging.warning("converting multivalues for attribute-filter.")
        a_options = convert.multivalue_to_unique(a_options)
    if a_filter and a_options and len([x for x in a_filter if x not in a_options]):
        a_filter = []
    # prepare data
    table = freqs_fig.data_table(df)
    df = freqs_fig.prep_data(corpora, attribute, a_filter, statistics, df)
    if df.empty:
        return html.P("Nothing to graph", className="lead"), table, []
    # draw figs
    is_choropleth = [corp_data.dt[c].get("choropleth", []) for c in corpora]
    if attribute in [y for x in is_choropleth for y in x]:
        graphs = freqs_batch.choropleth_batch(df)
    else:
        graphs = freqs_batch.bar_batch(df)
    return graphs, table, a_options


@dash.callback(
    Output("url-clipboard", "content"),
    Input("url-clipboard", "n_clicks"),
    State("corpora-picker", "value"),
    State("attribute-picker", "value"),
    State("attribute-filter", "value"),
    State("statistic-picker", "value"),
    State("query-input", "value"),
    State("crossfilter-picker", "value"),
    prevent_initial_call=True,
)
def copy_url(
    n_clicks, corpora, attribute, attribute_filter, statistics, input_text, crossfilter
):
    """Generates URL parameters based on current options."""

    if input_text and corpora and attribute and statistics:
        dt = {
            "query": input_text,
            "corpora": ";".join(corpora),
            "statistics": ";".join(statistics),
            "attribute": attribute,
            "crossfilter": crossfilter,
            "attribute_filter": ";".join(attribute_filter),
        }

        _url = (
            request.host_url.rstrip("/")
            + _path.strip("/")
            + "?"
            + urllib.parse.urlencode(dt)
        )
        logging.debug(_url)
        return _url


@dash.callback(
    Output("download-frequencies", "data"),
    Input("download-frequencies-button", "n_clicks"),
    State("corpora-picker", "value"),
    State("attribute-picker", "value"),
    State("query-input", "value"),
    State({"type": "Graph1", "group": ALL}, "clickData"),
    State("crossfilter-picker", "value"),
    prevent_initial_call=True,
)
def download_frequencies(
    n_clicks, corpora, attribute, input_text, clickdata, crossfilter
):
    """Prepares a file of the current data sample to download."""

    dfs = [
        _df_from_crossfilter(cd, crossfilter, None)
        for cd in clickdata
        if clickdata and crossfilter and cd
    ]
    dfs = [x[0] for x in dfs if x]
    df = send_requests(input_text, corpora, attribute)
    df = pd.concat(dfs + [df])

    if not df.empty:
        df["corpname"].replace(
            {k: corp_data.dt[k]["name"] for k in corp_data.dt.keys()}, inplace=True
        )
        df.drop(["params"], axis=1, inplace=True)
        df.reset_index(drop=True, inplace=True)
        file = "~".join(["~".join(df["corpname"].unique()), input_text, attribute])
        logging.debug(file)
        return dcc.send_data_frame(df.to_csv, file + ".csv")
