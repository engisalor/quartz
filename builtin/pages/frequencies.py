import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import sgex
from dash import Input, Output, State, dcc, get_app, html
from flask_caching import Cache

import environment.settings as env
from builtin.call import assemble, parse
from builtin.components.aio.aio import CollapsingContentAIO, MarkdownFileAIO

app = get_app()
cache = Cache(app.server, config=env.cache_config)


dash.register_page(__name__)


layout = html.Div(
    [
        html.H1("Frequencies"),
        html.P("Enter queries below and press enter to generate visualizations."),
        html.Br(),
        CollapsingContentAIO(
            "User guide", [MarkdownFileAIO("frequencies", "builtin/markdown")]
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H3("Query"),
                        dcc.Input(
                            id="query-input",
                            type="text",
                            placeholder="Enter a word or phrase",
                        ),
                    ],
                    style={"margin": "1rem"},
                ),
                html.Div(
                    [
                        html.H3("Corpora"),
                        dcc.Checklist(
                            [
                                {"label": v["name"], "value": k}
                                for k, v in env.corpora.items()
                            ],
                            [k for k in env.corpora.keys()],
                            id="corpora-picker",
                            style={"overflow": "scroll", "height": "75px"},
                        ),
                    ],
                    style={"margin": "1rem"},
                ),
                html.Div(
                    [
                        html.H3("Attribute"),
                        dcc.RadioItems(
                            id="attribute-picker",
                            style={"overflow": "scroll", "height": "75px"},
                        ),
                    ],
                    style={"margin": "1rem"},
                ),
            ],
            style={
                "display": "flex",
                "justify-content": "flex-start",
                "flex-wrap": "wrap",
            },
        ),
        html.Br(),
        dcc.Loading(
            id="loading",
            children=[html.Div([html.Div(id="loading-output")])],
            type="circle",
        ),
    ]
)


@cache.memoize()
def make_corpus_attr_options(corpus):
    params = sgex.parse("builtin/call/corp_info.yml")
    params["id"]["call"] |= {"corpname": corpus}
    params["id"]["meta"] = corpus
    sgex.Call(params, server=env.NOSKE_SERVER_NAME, loglevel="debug")
    info = parse.Corp_Info(corpus)
    info.df["attributes"] = info.df["structure"] + "." + info.df["name"]
    info.df.sort_values(["attributes"], inplace=True)
    return [{"label": x, "value": x} for x in info.df["attributes"].values]


@dash.callback(
    Output("attribute-picker", "options"),
    Output("attribute-picker", "value"),
    Input("corpora-picker", "value"),
    State("attribute-picker", "options"),
    State("attribute-picker", "value"),
)
def update_attribute_radio(corpora, options, value):
    if len(corpora) > 1:
        options = [{"label": x, "value": x} for x in env.comparable_attributes]
        return options, options[0]["value"]
    elif len(corpora) == 1:
        options = make_corpus_attr_options(corpora[0])
        return options, options[0]["value"]
    else:
        for option in options:
            option["disabled"] = True
        return options, value


def make_graph(data: parse.Freqs, y):
    data.df.sort_values("value", inplace=True)
    fig = px.bar(
        data.df,
        x="value",
        y=y,
        color="corpname",
        barmode="group",
        labels=env.labels,
        facet_col="nicearg",
        facet_col_wrap=1,
        height=len(data.df["nicearg"].unique()) * 300,
        hover_data={
            "corpname": False,
            "nicearg": False,
            "value": False,
            "rel": ":,",
            "reltt": ":,",
            "fpm": ":,",
            "frq": ":,",
        },
        category_orders={"corpname": sorted(data.df["corpname"].unique())},
    )

    fig.update_traces(textfont_size=12, textposition="outside", cliponaxis=False)

    fig.update_layout(
        plot_bgcolor="#ffffff",
        xaxis={"categoryorder": "category ascending"},
        hovermode="x unified",
    )
    return dcc.Graph(figure=fig)


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
    sgex.Call(calls, server=env.NOSKE_SERVER_NAME, loglevel="debug")
    params_list = [v["call"] for v in calls.values()]
    return parse.hash_calls(params_list)


def make_summary(df):
    summary = pd.DataFrame()
    for c in df["corpname"].unique():
        for q in df["nicearg"].unique():
            slice = df.query("corpname == @c and nicearg == @q")
            record = [
                {
                    "corpus": c,
                    "query": q,
                    "mean rel %": f'{slice["rel"].mean():,.2f}',
                    "mean reltt": f'{slice["reltt"].mean():,.2f}',
                    "mean fpm": f'{slice["fpm"].mean():,.2f}',
                    "mean frq": f'{slice["frq"].mean():,.2f}',
                    "total frq": f'{slice["frq"].sum():,}',
                }
            ]
            summary = pd.concat([summary, pd.DataFrame.from_records(record)])
    return summary


@cache.memoize()
def draw_page(data):
    table_props = {
        "striped": True,
        "bordered": True,
        "style": {"max-width": "800px"},
    }
    summary = make_summary(data.df)
    return html.Div(
        [
            html.H4(
                "Summary",
                title="""Summary:
- mean values for measures and the total frequency for each query in each corpus""",
            ),
            dbc.Table.from_dataframe(summary, **table_props),
            html.H4(
                "Relative density",
                title="""Relative density % (rel):
- how often a query appears in a text type compared to the whole corpus""",
            ),
            make_graph(data, y="rel"),
            html.H4(
                "Relative frequency per million in text type",
                title="""Relative frequency per million in text type (reltt):
- how often a query appears for every million words in a text type""",
            ),
            make_graph(data, y="reltt"),
            html.H4(
                "Frequency per million",
                title="""Frequency per million (fpm):
- how often a query appears for every million words in a corpus""",
            ),
            make_graph(data, y="fpm"),
            html.H4(
                "Occurrences",
                title="""Occurrences (frq):
- how often a query appears in a corpus""",
            ),
            make_graph(data, y="frq"),
        ]
    )


@dash.callback(
    Output("loading-output", "children"),
    Input("query-input", "n_submit"),
    Input("corpora-picker", "value"),
    Input("attribute-picker", "value"),
    State("query-input", "value"),
    prevent_initial_call=True,
)
def update_output(n_submit, corpora, attribute, input_text):
    result = html.Div([])
    if isinstance(input_text, str):
        input_text = input_text.strip()
    if input_text and corpora and attribute:
        call_hashes = make_calls(corpora, attribute, input_text)
        data = parse.Freqs(call_hashes)
        result = draw_page(data)
    return result
