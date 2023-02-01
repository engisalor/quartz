import dash
import plotly.express as px
import sgex
from dash import Input, Output, dcc, get_app, html
from flask_caching import Cache

from builtin.call import parse
from builtin.components.aio.aio import MarkdownFileAIO
from environment.settings import NOSKE_SERVER_NAME, cache_config

app = get_app()
cache = Cache(app.server, config=cache_config)


dash.register_page(__name__)


layout = html.Div(
    [
        MarkdownFileAIO("frequencies", "builtin/markdown"),
        html.Br(),
        dcc.Input(
            id="query-input",
            type="text",
            placeholder="Enter a word or phrase",
            debounce=True,
        ),
        html.Br(),
        html.Div(children=dcc.Graph(), id="frequency-graph"),
    ]
)


@dash.callback(
    Output("frequency-graph", "children"),
    Input("query-input", "value"),
    prevent_initial_callback=True,
)
@cache.memoize()
def update_output(input):
    if input:
        input = input.strip()
        queries = [x.strip() for x in input.split(";")]
        file = "builtin/call/freqs.yml"
        dt = sgex.parse(file)
        dt[file] = dt.pop("id")

        for query in queries:
            query_cql = [
                f'[lc="{x.strip()}" | lemma_lc="{x.strip()}"]' for x in query.split()
            ]
            struct = "doc"
            ttypes = ["date__original__year"]
            meta = f"simple {query}"
            params = {
                "q": ["q" + "".join(query_cql)],
                "corpname": "reliefweb_en",
                "freq_sort": "freq",
                "fcrit": [f"{struct}.{x} 0" for x in ttypes],
            }
            dt[file]["call"] |= params
            dt[file]["meta"] = meta
            sgex.Call(dt, server=NOSKE_SERVER_NAME, loglevel="debug")

        data = parse.Freqs([f"simple {query}" for query in queries])
        if not data.df.empty:
            fig_rel = px.line(
                data.df, x="value", y="rel", color="nicearg", title="Relative frequency"
            )
            fig_fpm = px.line(
                data.df,
                x="value",
                y="fpm",
                color="nicearg",
                title="Frequency per million",
            )
            return html.Div(
                [
                    dcc.Graph(figure=fig_rel),
                    dcc.Graph(figure=fig_fpm),
                ]
            )
        else:
            return html.Div([html.Br(), html.P("Nothing found.")])
