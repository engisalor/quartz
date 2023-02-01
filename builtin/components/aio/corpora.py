import uuid

import dash_bootstrap_components as dbc
import plotly.express as px
import sgex
from dash import MATCH, Input, Output, State, callback, dcc, get_app, html
from flask_caching import Cache

import environment.settings as env
from builtin.call import parse
from builtin.components.aio.aio import MarkdownFileAIO

app = get_app()
cache = Cache(app.server, config=env.cache_config)


class CorpusDetailsAIO(html.Div):
    class ids:
        def store(aio_id):
            return {
                "component": "CorpusDetailsAIO",
                "subcomponent": "store",
                "aio_id": aio_id,
            }

        def dropdown(aio_id):
            return {
                "component": "CorpusDetailsAIO",
                "subcomponent": "dropdown",
                "aio_id": aio_id,
            }

        def graph(aio_id):
            return {
                "component": "CorpusDetailsAIO",
                "subcomponent": "graph",
                "aio_id": aio_id,
            }

    ids = ids

    def __init__(
        self,
        meta,
        aio_id: str = None,
    ):

        if aio_id is None:
            aio_id = str(uuid.uuid4())

        super().__init__(
            [
                html.H4("Attribute details"),
                html.Div(meta, id=self.ids.store(aio_id), hidden=True),
                html.Div(
                    dcc.Dropdown(
                        clearable=False,
                        id=self.ids.dropdown(aio_id),
                    ),
                    style={"max-width": "400px"},
                ),
                dcc.Graph(id=self.ids.graph(aio_id)),
            ]
        )

    @callback(
        Output(ids.dropdown(MATCH), "options"),
        Output(ids.dropdown(MATCH), "value"),
        Input(ids.store(MATCH), "children"),
    )
    def attribute_chart(meta):
        wordlist = parse.Wordlist(f"ttype_analysis {meta}")
        attrs = []
        for attr in wordlist.df["attribute"].unique():
            n_unique = len(wordlist.df.query("attribute == @attr"))
            if n_unique >= 2:
                attrs.append(attr)
        attrs = sorted(attrs)
        return attrs, attrs[0]

    @callback(
        Output(ids.graph(MATCH), "figure"),
        Input(ids.dropdown(MATCH), "value"),
        State(ids.store(MATCH), "children"),
    )
    def generate_chart(attribute, meta):
        wordlist = parse.Wordlist(f"ttype_analysis {meta}")
        df = wordlist.df.query("attribute == @attribute")

        # indicate whether pie chart includes all values
        dt = sgex.parse("builtin/call/ttype_analysis.yml")
        top_n = dt["id"]["call"]["wlmaxitems"]
        if top_n > len(df):
            title = f"All values for {attribute}"
        else:
            title = f"Top {len(df)} values for {attribute}"

        fig = px.pie(df, values="frq", names="str", hole=0.3, title=title)
        fig.update_traces(textposition="inside")
        fig.update_layout(uniformtext_minsize=12, uniformtext_mode="hide")
        fig.update_traces(hoverinfo="all")
        return fig


class CorpusOverviewAIO(html.Div):
    class ids:
        def store(aio_id):
            return {
                "component": "CorpusOverviewAIO",
                "subcomponent": "store",
                "aio_id": aio_id,
            }

        def dbc_button(aio_id):
            return {
                "component": "CorpusOverviewAIO",
                "subcomponent": "dbc_button",
                "aio_id": aio_id,
            }

        def dbc_collapse(aio_id):
            return {
                "component": "CorpusOverviewAIO",
                "subcomponent": "dbc_collapse",
                "aio_id": aio_id,
            }

    ids = ids

    def __init__(
        self,
        corpus: str,
        aio_id: str = None,
    ):

        if aio_id is None:
            aio_id = str(uuid.uuid4())

        button_props = {
            "color": "light",
            "n_clicks": 0,
            "className": "mb-3",
            "size": "lg",
        }

        super().__init__(
            [
                dcc.Store(
                    data={"corpus": corpus},
                    id=self.ids.store(aio_id),
                    storage_type="session",
                ),
                dbc.Button(corpus, id=self.ids.dbc_button(aio_id), **button_props),
                dbc.Collapse([], id=self.ids.dbc_collapse(aio_id)),
            ]
        )

    @callback(
        Output(ids.dbc_collapse(MATCH), "is_open"),
        Input(ids.dbc_button(MATCH), "n_clicks"),
        State(ids.dbc_collapse(MATCH), "is_open"),
    )
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open

    @callback(
        Output(ids.dbc_collapse(MATCH), "children"),
        Input(ids.dbc_button(MATCH), "n_clicks"),
        State(ids.store(MATCH), "data"),
        prevent_initial_call=True,
    )
    def show_corp_info(n_clicks, data):
        table_props = {
            "striped": True,
            "bordered": True,
            "style": {"max-width": "200px"},
        }

        @cache.memoize()
        def get_info(data):
            # get text basic corpus info
            params = sgex.parse("builtin/call/corp_info.yml")
            params["id"]["call"] |= {"corpname": data["corpus"]}
            params["id"]["meta"] = data["corpus"]
            sgex.Call(params, server=env.NOSKE_SERVER_NAME, loglevel="debug")
            info = parse.Corp_Info(data["corpus"])
            info.df["size"] = info.df["size"].apply(lambda x: f"{x:,}")
            # get text type analysis
            wlattrs = info.df["structure"] + "." + info.df["name"]
            for wlattr in wlattrs:
                params = sgex.parse("builtin/call/ttype_analysis.yml")
                params["id"]["call"] |= {"corpname": info.meta, "wlattr": wlattr}
                params["id"]["meta"] = f"ttype_analysis {info.meta}"
                sgex.Call(params, server=env.NOSKE_SERVER_NAME, loglevel="debug")
            return info

        info = get_info(data)

        return [
            MarkdownFileAIO(info.meta),
            html.H3("Sizes"),
            dbc.Table.from_dataframe(
                info.sizes.sort_values("size", ascending=False), **table_props
            ),
            html.H3("Attributes"),
            dbc.Table.from_dataframe(info.df, **table_props),
            CorpusDetailsAIO(info.meta),
        ]
