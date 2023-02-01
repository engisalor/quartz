import datetime
import pathlib

import dash
import sgex
from dash import dcc, get_app, html
from dash.dependencies import Input, Output
from flask_caching import Cache

from builtin.utils import decorator
from builtin.version import version
from environment.settings import NOSKE_SERVER_NAME, cache_config

app = get_app()
cache = Cache(app.server, config=cache_config)


dash.register_page(__name__)

layout = html.Div(
    [
        html.H1("Debug"),
        html.Hr(),
        html.H2("Settings"),
        html.P(["Version: ", version]),
        html.Button("storage", id="check-storage"),
        html.Div(id="check-storage-out", children=""),
        html.H2("Performance"),
        html.Button("CPU", id="check-cpu"),
        html.Div(id="check-cpu-out", children=""),
        html.H2("API connections"),
        html.Button("NoSkE", id="check-noske"),
        html.Div(id="check-noske-out", children=""),
        html.H2("Caching"),
        html.Div(id="flask-cache-memoized-children"),
        dcc.RadioItems(
            [f"Option {i}" for i in range(1, 4)],
            "Option 1",
            id="flask-cache-memoized-dropdown",
        ),
        html.Div(
            f'Results are cached for {cache_config["CACHE_DEFAULT_TIMEOUT"]} seconds'
        ),
    ]
)


@dash.callback(
    Output("check-noske-out", "children"),
    Input("check-noske", "n_clicks"),
    prevent_initial_call=True,
)
def check_noske(n_clicks):
    params = {"debug": {"type": "corp_info", "call": {"corpname": "susanne"}}}
    job = sgex.Call(params, server=NOSKE_SERVER_NAME, output="json", loglevel="debug")
    return html.Div(
        [
            html.P(f"Clicks: {n_clicks}"),
            html.P(f"{str(params)}"),
            html.P(f"{str(job.data)}"),
        ]
    )


@dash.callback(
    Output("check-storage-out", "children"),
    Input("check-storage", "n_clicks"),
    prevent_initial_call=True,
)
def check_storage(n_clicks):
    cwd = pathlib.Path.cwd()
    files = pathlib.Path("data").glob("*")
    files = [x.name for x in files if x]

    return html.Div(
        [
            html.P(f"Clicks: {n_clicks}"),
            html.P(f"Path: {cwd}"),
            html.P(f"Data:\t{files}"),
        ]
    )


@dash.callback(
    Output("check-cpu-out", "children"),
    Input("check-cpu", "n_clicks"),
    prevent_initial_call=True,
)
def check_cpu(n_clicks):
    @decorator.timer
    def slow_func(size):
        ls = []
        for x in range(size):
            ls.append("a")

    _, t = slow_func(10000000)
    return html.Div([html.P(f"Clicks: {n_clicks}"), html.P(f"Execution time: {t}")])


@dash.callback(
    Output("flask-cache-memoized-children", "children"),
    Input("flask-cache-memoized-dropdown", "value"),
    prevent_initial_call=True,
)
@cache.memoize()
def render(value):
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    return f'Selected "{value}" at "{current_time}"'
