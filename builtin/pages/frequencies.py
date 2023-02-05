import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import sgex
from dash import Input, Output, State, dcc, get_app, html
from flask_caching import Cache

import environment.settings as env
from builtin.call import assemble, parse
from builtin.components.aio.aio import MarkdownFileAIO

app = get_app()
cache = Cache(app.server, config=env.cache_config)


dash.register_page(__name__)


layout = html.Div(
    [
        MarkdownFileAIO("frequencies", "builtin/markdown"),
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
        html.Div(children=dcc.Graph(), id="frequency-graph"),
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
    background=True,
    running=[
        (Output("query-input", "disabled"), True, False),
    ],
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


@cache.memoize()
def make_graph(data: parse.Freqs, y="reltt"):
    # df = data.df.query("corpname in @corpora")

    # NOTE patch for hejuly2019_backup date formatting inconsistencies
    # if attribute in ["date", "class.DATE"]:
    #     df["value"] = [
    #       x.strip() if not "-" in x else x[-4:].strip() for x in df["value"]
    #       ]

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
            "fpm": False,
            "frq": ":,",
            "rel": ":,",
            "reltt": ":,",
        },
        category_orders={"corpname": sorted(data.df["corpname"].unique())},
    )

    # for corpus in data.df["corpname"].unique():
    #     stat = data.df.loc[data.df["corpname"] == corpus, y].mean()
    #     fig.add_hline(
    #         y=stat,
    #         annotation_text=f"{corpus} mean={stat.round(2)}",
    #         line_dash="dot",
    #         row="all", col="all")

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


@dash.callback(
    Output("frequency-graph", "children"),
    Input("query-input", "n_submit"),
    Input("corpora-picker", "value"),
    Input("attribute-picker", "value"),
    State("query-input", "value"),
    prevent_initial_callback=True,
    background=True,
    running=[
        (Output("query-input", "disabled"), True, False),
    ],
)
def update_output(n_submit, corpora, attribute, input_text):
    if isinstance(input_text, str):
        input_text = input_text.strip()
    if input_text and corpora and attribute:
        call_hashes = make_calls(corpora, attribute, input_text)
        data = parse.Freqs(call_hashes)
        summary = []
        for corpus in data.df["corpname"].unique():
            summary.append(
                {
                    "corpus": corpus,
                    "mean rel": data.df.loc[
                        data.df["corpname"] == corpus, "rel"
                    ].mean(),
                    "mean reltt": data.df.loc[
                        data.df["corpname"] == corpus, "reltt"
                    ].mean(),
                    "mean fpm": data.df.loc[
                        data.df["corpname"] == corpus, "fpm"
                    ].mean(),
                    "total frq": data.df.loc[
                        data.df["corpname"] == corpus, "frq"
                    ].sum(),
                }
            )
        summary_df = pd.DataFrame.from_records(summary).round(2)
        summary_df["mean rel"] = summary_df["mean rel"].apply(lambda x: f"{x:,.2f}")
        summary_df["mean reltt"] = summary_df["mean reltt"].apply(lambda x: f"{x:,.2f}")
        summary_df["mean fpm"] = summary_df["mean fpm"].apply(lambda x: f"{x:,.2f}")
        summary_df["total frq"] = summary_df["total frq"].apply(lambda x: f"{x:,}")
        summary_df.sort_values("corpus", inplace=True)

        table_props = {
            "striped": True,
            "bordered": True,
            "style": {"max-width": "600px"},
        }

        return html.Div(
            [
                html.H4(
                    "Summary table",
                    title="""
Mean values for relative measures and the total frequency
for the query in each corpus.""",
                ),
                dbc.Table.from_dataframe(summary_df, **table_props),
                html.H4(
                    "Relative density",
                    title="""
Relative density (rel) describes how often a query
appears in a corpus text type/attribute. This is measured as a
percentage, where 100% indicates a query appears just as often
in a text type as it does in the whole corpus.""",
                ),
                make_graph(data, y="rel"),
                html.H4(
                    "Relative frequency per million in text type",
                    title="""
Relative frequency per million (reltt) describes how
many times a query appears for every million words in a text
type. This can be used to compare the density of a query between
corpora.""",
                ),
                make_graph(data, y="reltt"),
                html.H4(
                    "Frequency per million",
                    title="""
Frequency per million (fpm) describes how many times a
query appears for every million words in a corpus. This is also
called normalized frequency and can be used to compare the
density of a query between corpora.""",
                ),
                make_graph(data, y="fpm"),
                html.H4(
                    "Occurrences",
                    title="""
Occurrences (frq) refers to the number of times a query
appears in the corpus, i.e., the absolute frequency.""",
                ),
                make_graph(data, y="frq"),
            ]
        )
    else:
        return dcc.Graph()


# comparable text types should use RW subcorpus
