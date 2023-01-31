import dash
import plotly.express as px
import sgex
from dash import Input, Output, dcc, html

from builtin.call import parse
from environment.settings import NOSKE_SERVER_NAME

dash.register_page(__name__)


layout = html.Div(
    [
        dcc.Input(
            id="query-input",
            type="text",
            placeholder="Enter a word or phrase",
            debounce=True,
        ),
        html.Div(children=dcc.Graph(), id="frequency-graph"),
    ]
)


@dash.callback(
    Output("frequency-graph", "children"),
    Input("query-input", "value"),
    prevent_initial_callback=True,
)
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
        fig = px.line(data.df, x="value", y="rel", color="nicearg")
        return dcc.Graph(figure=fig)
