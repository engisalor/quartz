import logging
import pathlib
import urllib
from time import perf_counter

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import sgex
from dash import Input, Output, State, ctx, dcc, get_app, html
from flask import request

import environment.settings as env
from builtin.components.aio import aio
from builtin.utils import convert, redirect

app = get_app()

page_name = pathlib.Path(__file__).stem
dash.register_page(__name__)


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
                style={"minWidth": "100px", "flexGrow": 2},
            ),
        ],
    )

    corpora_box = html.Div(
        [
            aio.PopoverHeaderAIO("Corpora", title="Select which corpus/corpora to use"),
            dcc.Checklist(
                options=[
                    {"label": v["name"], "value": k} for k, v in env.corpora.items()
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
                options=[{"label": v, "value": k} for k, v in env.statistics.items()],
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
                dbc.PopoverBody(aio.MarkdownFileAIO("builtin/markdown/user_guide.md")),
                target="guide-button",
                trigger="click",
                style={"overflow": "scroll"},
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
            html.H1("Frequencies"),
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

    if len(corpora) > 1:
        options = [{"label": x, "value": x} for x in env.comparable_attributes]
    elif len(corpora) == 1:
        df = env.premade_calls[corpora[0]]["structures_df"].copy()
        df["options"] = df["structure"] + "." + df["attribute"]
        df.sort_values(["options"], inplace=True)
        options = [{"label": x, "value": x} for x in df["options"].values]
    else:
        options, value = [], None
    value = set_attribute_value(options, value)
    logging.debug(f"V={value} len(O)={len(options)}")
    return options, value


def make_attribute_filter_options(corpora, attribute):
    """Returns attribute filter options for selected corpora.

    TODO
        Managing multivalues:
            Currently assumes `|` is the multisep for all corpora
            and that all attributes are multivalues. Can cause unwanted
            results if `|` appears in single values. To fix, must parse
            each corpus's config file and adapt behavior to each
            (may not be possible for some third party corpora).
    """

    options = []
    for corpus in corpora:
        attr = attribute  # noqa: F841
        if attribute in env.comparable_attributes:
            attr = env.corpora[corpus]["comparable_attributes"][attribute]  # noqa: F841
        slice = (
            env.premade_calls[corpus]["ttypes_df"].query("attribute == @attr").copy()
        )
        slice.sort_values("str", inplace=True)
        o = convert.multivalue_to_unique(slice["str"].unique(), "|")
        options.extend(o)
    return sorted(list(set(options)))


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
    """Controls attribute filters."""
    # default to nothing
    if not attribute or not corpora:
        logging.debug("empty")
        return [], []
    else:
        options = make_attribute_filter_options(corpora, attribute)
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


def footnote(letter, text):
    return html.P([html.Sup(letter), text], className="footnote")


def table(dataframe, args_map: list):
    """Builds a table of summary statistics."""

    df = pd.DataFrame()
    for c in dataframe["corpname"].unique():
        corpus = env.corpora[c].get("name")
        for arg_map in args_map:
            nicearg = arg_map[1]  # noqa: F841
            slice = dataframe.query("corpname == @c and nicearg == @nicearg")
            total_frq = slice["total_frq"].unique()
            if len(total_frq) == 1:
                total_frq = f"{total_frq[0]:,}"
            fpmcorp = slice["total_fpm"].unique()
            if len(fpmcorp) == 1:
                fpmcorp = f"{fpmcorp[0]:,}"
            record = [
                {
                    "corpus": corpus,
                    "query": arg_map[0],
                    "attribute": slice["attribute"].unique(),
                    "n attr.": f'{slice["value"].count():,}',
                    "frq corp.": total_frq,
                    "frq attr.": f'{slice["frq"].sum():,}',
                    "fpm corp.": fpmcorp,
                    "M rel %": f'{slice["rel"].mean():,.2f}',
                    "M reltt": f'{slice["reltt"].mean():,.2f}',
                    "M fpm": f'{slice["fpm"].mean():,.2f}',
                    "M frq": f'{slice["frq"].mean():,.2f}',
                }
            ]
            df = pd.concat([df, pd.DataFrame.from_records(record)])

    column_mapping = {}
    footnotes = [
        "n attr.",
        "frq corp.",
        "frq attr.",
        "fpm corp.",
        "M rel %",
        "M reltt",
        "M fpm",
        "M frq",
    ]
    number = 0
    for col in df.columns:
        if col not in footnotes:
            column_mapping[col] = html.Small(col)
        else:
            number += 1
            column_mapping[col] = html.Small([col, html.Sup(number)])
    df.rename(column_mapping, axis=1, inplace=True)
    fmaxitems = "|".join(slice["fmaxitems"].unique())
    maxitems_note = f"(5 years, 12 themes, etc., up to the {fmaxitems} most common)"

    return html.Div(
        [
            dbc.Table.from_dataframe(df, striped=True, bordered=True),
            footnote(1, f"Number of text types {maxitems_note}"),
            footnote(2, "Occurrences in the whole corpus"),
            footnote(3, "Sum of occurrences in each attribute"),
            footnote(4, "Frequency per million tokens in the whole corpus"),
            footnote(5, "Mean relative density in text types"),
            footnote(6, "Mean relative density per million in text types"),
            footnote(7, "Mean frequency per million in text types"),
            footnote(8, "Mean occurrences in text types"),
        ]
    )


def graph(df: pd.DataFrame, arg_map: list):
    """Builds bar graphs for given dataframe and query/nicearg."""

    nicearg = arg_map[1]  # noqa: F841
    df = df.query("nicearg == @nicearg").copy()
    df["corpus"] = df["corpname"].copy()
    df["corpus"].replace(env.labels, inplace=True)

    fig = px.bar(
        df,
        x="value",
        y="f",
        color="corpus",
        barmode="group",
        labels=env.labels,
        facet_col="statistic",
        facet_col_wrap=1,
        facet_row_spacing=0.1,
        title=arg_map[0],
        height=len(df["statistic"].unique()) * 150 + 140,
        hover_data={
            "corpus": False,
            "corpname": False,
            "nicearg": False,
            "value": False,
            "statistic": False,
            "f": ":,",
        },
        category_orders={"corpname": sorted(df["corpname"].unique())},
    )
    fig.update_layout(
        plot_bgcolor="#ffffff",
        xaxis={"categoryorder": "category ascending"},
        hovermode="x",
        title_font_size=24,
        xaxis_title=" & ".join(df["attribute"].unique()),
    )
    fig.update_yaxes(matches=None)

    def customize_annotation(annotation):
        text = annotation.text.split("=")[-1]
        if text in env.labels.keys():
            text = env.labels[text]
        annotation.update(
            text=text,
            font_size=16,
        )

    fig.for_each_annotation(customize_annotation)
    logging.debug(f"MADE {df.size}")
    return dcc.Graph(figure=fig)


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
    t0 = perf_counter()
    df = pd.DataFrame.from_dict(data)
    if not len(statistics):
        return html.Div(), html.Div()
    if df.empty:
        return html.Div(), html.Div()
    query_args = []
    slice = pd.DataFrame()
    _graph = []
    _table = []
    attrs = []
    # filtering
    if len(corpora):
        query_args.append("corpname in @corpora")
    if attribute in env.comparable_attributes:
        attrs = [  # noqa: F841
            env.corpora[c].get("comparable_attributes", {}).get(attribute, None)
            for c in corpora
        ]
    else:
        attrs = [attribute]  # noqa: F841

    query_args.append("attribute in @attrs")
    if len(attribute_filter):
        query_args.append("value in @attribute_filter")
    if len(query_args):
        slice = df.query(" and ".join(query_args)).copy()
    else:
        slice = df.copy()
    # melting statistics
    melted_slice = slice.melt(
        id_vars=[x for x in slice.columns if x not in env.statistics.keys()],
        var_name="statistic",
        value_name="f",
    )
    melted_slice.query("statistic in @statistics", inplace=True)
    melted_slice.sort_values("value", inplace=True)
    niceargs = melted_slice["nicearg"].unique().tolist()
    args = input_text.split(";")
    if len(niceargs) != len(args):
        return html.Div(), html.Div()
    args_map = [[args[x], niceargs[x]] for x in range(len(args))]
    if not melted_slice.empty:
        _graph = [graph(melted_slice, arg_map) for arg_map in args_map]
        _table = table(df, args_map)
    t1 = perf_counter()
    m = f"{corpora} {attribute} {attribute_filter}"
    logging.debug(f"graph and table: {t1-t0:.3}s {len(slice)} rows, {m}")
    return html.Div(_graph), _table


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
    t0 = perf_counter()
    if isinstance(input_text, str):
        input_text = input_text.strip()
    if not input_text:
        return {}
    if not len(corpora):
        return {}
    if not attribute:
        return {}

    max_queries = 3
    queries = [x.strip() for x in input_text.split(";") if x.strip()]
    dfs = pd.DataFrame()
    for corpus in corpora:
        calls = []
        if attribute in env.comparable_attributes:
            attr = env.corpora[corpus]["comparable_attributes"][attribute]
        else:
            attr = attribute
        for query in queries[:max_queries]:
            query = query.strip()
            if query.startswith("q,") and len(query) > 2:
                query = "aword," + query[2:]
            else:
                query = env.simple_query_escape(query)
                query = sgex.simple_query(query)
            calls.append(
                sgex.Freqs(
                    {
                        "q": query,
                        "corpname": corpus,
                        "fcrit": f"{attr} 0",
                        "freq_sort": "freq",
                        "fmaxitems": 50,
                        "fpage": 1,
                        "group": 0,
                        "showpoc": 1,
                        "showreltt": 1,
                        "showrel": 1,
                    }
                )
            )
        package = sgex.Package(
            calls,
            env.SGEX_SERVER,
            env.SGEX_CONFIG,
            session_params=env.session_params,
            halt=False,
        )
        package.send_requests()
        dfs = pd.concat(
            [dfs] + [sgex.parse.freqs.freqs_json(r) for r in package.responses]
        )
    t1 = perf_counter()
    logging.debug(f"{t1-t0:.3}s {len(queries)} calls")
    return dfs.to_dict("records")


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
        if len(";".join(attribute_filter)) > 500:
            logging.debug("long url: removing attribute-filter")
            dt.pop("attribute_filter", None)

        url = request.host_url + page_name + "?" + urllib.parse.urlencode(dt)
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
    df = pd.DataFrame.from_dict(data)
    df["corpname"].replace(env.labels, inplace=True)
    df.reset_index(drop=True, inplace=True)
    file = "~".join(["~".join(df["corpname"].unique()), query, attribute])
    logging.debug(file)
    return dcc.send_data_frame(df.to_csv, file + ".csv")
