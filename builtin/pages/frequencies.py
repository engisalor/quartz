import logging
import urllib

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Input, Output, State, ctx, dcc, get_app, html
from flask_caching import Cache

import environment.settings as env
from builtin.call import call, parse
from builtin.components.aio import aio
from builtin.utils import convert, io, redirect

app = get_app()
cache = Cache(app.server, config=env.cache_config)

dash.register_page(__name__)


def layout(
    query="", corpora="", statistics="rel", attribute="", attribute_filter="", **args
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
                title=io.load_markdown(
                    "builtin/markdown/documentation/01-query-intro.md"
                ),
            ),
            dbc.Input(
                value=query,
                id="query-input",
                placeholder="Enter a word or phrase",
                style={"minWidth": "100px"},
            ),
        ],
    )

    corpora_box = html.Div(
        [
            aio.PopoverHeaderWithTitle(
                "Corpora", file="builtin/markdown/documentation/02-corpora.md"
            ),
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

    stats_title = [
        io.load_markdown(x)
        for x in [
            "builtin/markdown/documentation/07-frq-intro.md",
            "builtin/markdown/documentation/08-rel-intro.md",
            "builtin/markdown/documentation/09-fpm-intro.md",
            "builtin/markdown/documentation/10-reltt-intro.md",
        ]
    ]

    stats_box = html.Div(
        [
            aio.PopoverHeaderWithTitle(
                "Statistics",
                title="\n".join(["Selecting statistics\n"] + stats_title),
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
            aio.PopoverHeaderWithTitle(
                "Attributes",
                file="builtin/markdown/documentation/03-attribute-intro.md",
            ),
            dcc.RadioItems(
                value=attribute, id="attribute-picker", className="settings-options"
            ),
        ]
    )

    filter_box = html.Div(
        [
            aio.PopoverHeaderWithTitle(
                "Attributes filter",
                file="builtin/markdown/documentation/03.1-attribute-filter.md",
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
                title="Click to show/hide settings",
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
            # dcc.Clipboard(
            #     title="Copy URL for current settings",
            #     id="url-clipboard"),
            # html.I(id="reset-button",
            #     className="bi bi-arrow-clockwise", title="Reset"),
            dcc.Location(id="url", refresh=False),
            # dcc.Location(id="url-refresh", refresh=True),
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
            html.H1("Frequencies"),
            top_panel,
            dbc.Collapse(
                html.Div(id="table"),
                id="table-collapse",
                is_open=False,
            ),
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
        options = call.make_corpus_attr_options(corpora[0])
    else:
        options, value = [], None
    return options, set_attribute_value(options, value)


@cache.memoize()
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
    df = pd.DataFrame()
    for corpus in corpora:
        attr = attribute  # noqa: F841
        if attribute in env.comparable_attributes:
            attr = env.corpora[corpus][attribute]  # noqa: F841
        wordlist = parse.Wordlist(f"ttype_analysis {corpus}")
        df = pd.concat([df, wordlist.df])
        slice = df.query("attribute == @attr").copy()
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
    """Controls attribute filters.

    TODO
        Drawing graphs fails for certain long, multiword filter values (esp. urls,
        titles); may be related to attributes with many more values than ``fmaxitems``.
    """

    # default to nothing
    if not attribute or not corpora:
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


def error_check(input_text, corpora, attribute):
    """Displays custom error messages to user."""

    # non-empty values (redundant)
    components = {"query": input_text, "corpora": corpora, "attribute": attribute}
    for k, v in components.items():
        if not v:
            return dbc.Alert(f"Select a {k}", color="info")
    # too many simultaneous queries
    if input_text.count(";") > 3:
        msg = "Too many queries: the maximum is 4 (e.g., `one;two;three;four`)"
        return dbc.Alert(msg, color="info", style={"display": "inline-flex"})
    return None


def footnote(letter, text):
    return html.P([html.Sup(letter), text], className="footnote")


@cache.memoize()
def table(dataframe):
    """Builds a table of summary statistics."""

    df = pd.DataFrame()
    for c in dataframe["corpname"].unique():
        for q in dataframe["nicearg"].unique():
            slice = dataframe.query("corpname == @c and nicearg == @q")
            size = slice["total_size"].unique()
            if len(size) == 1:
                size = f"{size[0]:,}"
            fpmcorp = slice["total_fpm"].unique()
            if len(fpmcorp) == 1:
                fpmcorp = f"{fpmcorp[0]:,}"
            record = [
                {
                    "corpus": c,
                    "query": q,
                    "attribute": slice["attribute"].unique(),
                    "n attr.": f'{slice["value"].count():,}',
                    "frq corp.": size,
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
    footnotes = ["n attr.", "frq corp.", "frq attr.", "fpm corp."]
    number = 0
    for col in df.columns:
        if col not in footnotes:
            column_mapping[col] = html.Small(col)
        else:
            number += 1
            column_mapping[col] = html.Small([col, html.Sup(number)])
    df.rename(column_mapping, axis=1, inplace=True)
    fmaxitems = "|".join(slice["fmaxitems"].unique())

    return html.Div(
        [
            dbc.Table.from_dataframe(df, striped=True, bordered=True),
            footnote(1, f"Maximum attributes shown: {fmaxitems}"),
            footnote(2, "Total occurrences in a corpus"),
            footnote(3, "Sum of occurrences in each attribute"),
            footnote(4, "Total frequency per million in a corpus"),
            footnote(
                "", "Other columns show an attribute's mean value for each statistic"
            ),
        ]
    )


@cache.memoize()
def graph(data: parse.Freqs, nicearg: str):
    """Builds bar graphs for given dataframe and query/nicearg."""

    df = data.df.query("nicearg == @nicearg")
    fig = px.bar(
        df,
        x="value",
        y="f",
        color="corpname",
        barmode="group",
        labels=env.labels,
        facet_col="statistic",
        facet_col_wrap=1,
        title=nicearg,
        height=len(df["statistic"].unique()) * 150 + 140,
        hover_data={
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
    )
    fig.update_yaxes(matches=None)
    fig.update_traces(textfont_size=16, textposition="outside", cliponaxis=False)
    return dcc.Graph(figure=fig)


@dash.callback(
    Output("frequencies-content", "children"),
    Output("table", "children"),
    Input("query-input", "n_submit"),
    Input("corpora-picker", "value"),
    Input("attribute-picker", "value"),
    Input("attribute-filter", "value"),
    Input("statistic-picker", "value"),
    Input("query-button", "n_clicks"),
    State("query-input", "value"),
    prevent_initial_call=True,
)
def draw(
    n_submit, corpora, attribute, attribute_filter, statistics, n_clicks, input_text
):
    """Draws page content based on options."""

    # default to display nothing
    _graph, _table = [html.Div()] * 2
    # clean input text
    if isinstance(input_text, str):
        input_text = input_text.strip()
    # draw page
    if input_text and corpora and attribute:
        error = error_check(input_text, corpora, attribute)
        if error:
            return error, html.Div()
        call_hashes = call.make_calls(corpora, attribute, input_text)
        data = parse.Freqs(call_hashes)
        df_original = data.df.copy()
        data.df = data.df.melt(
            id_vars=[x for x in data.df.columns if x not in env.statistics.keys()],
            var_name="statistic",
            value_name="f",
        )
        data.df.sort_values("value", inplace=True)
        if attribute_filter:
            data.df = data.df.query("value in @attribute_filter")
        data.df = data.df.query("statistic in @statistics")
        niceargs = data.df["nicearg"].unique().tolist()
        _graph = [graph(data, arg) for arg in sorted(niceargs)]
        _table = table(df_original)
    return html.Div(_graph), _table


@dash.callback(
    Output("url", "search"),
    Input("query-input", "n_submit"),
    Input("corpora-picker", "value"),
    Input("attribute-picker", "value"),
    Input("attribute-filter", "value"),
    Input("statistic-picker", "value"),
    Input("query-button", "n_clicks"),
    State("query-input", "value"),
    prevent_initial_call=True,
)
def update_url(
    n_submit, corpora, attribute, attribute_filter, statistics, n_clicks, input_text
):
    """Generates current URL parameters based on current options."""

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
        return "?" + urllib.parse.urlencode(dt)


# FIXME not updating to current query
# @dash.callback(
#     Output("url-clipboard", "content"),
#     Input("url-clipboard", "n_clicks"),
#     State("url", "href"),
#     prevent_initial_call=True,
# )
# def update_url_clipboard(n_clicks, href):
#     return href


# FIXME not working reliably
# @dash.callback(
#     Output("url-refresh", "search"),
#     Input("reset-button", "n_clicks"),
#     prevent_initial_call=True,
# )
# def reset_url(n_clicks):
#     return ""


@dash.callback(
    Output("download-frequencies", "data"),
    Input("download-frequencies-button", "n_clicks"),
    State("corpora-picker", "value"),
    State("attribute-picker", "value"),
    State("query-input", "value"),
    prevent_initial_call=True,
)
def download_frequencies(n_clicks, corpora, attribute, query):
    """Prepares a file of the current data sample to download."""

    call_hashes = call.make_calls(corpora, attribute, query)
    data = parse.Freqs(call_hashes)
    data.df.reset_index(drop=True, inplace=True)
    file = "~".join([query, "~".join(corpora), attribute])
    return dcc.send_data_frame(data.df.to_csv, file + ".csv")
