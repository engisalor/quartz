import pathlib

import dash
import sgex
from dash import html
from dash.dependencies import Input, Output

from builtin.utils import decorator
from builtin.version import version
from environment.settings import NOSKE_SERVER_NAME

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
    Output("check-storage-out", "children"), Input("check-storage", "n_clicks")
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
