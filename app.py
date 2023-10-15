import importlib
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import flask
from dash import html

from builtin.utils import redirect
from settings import env

layout = importlib.import_module(env.ACTIVE_DIR.name.strip("/") + ".layout.layout")
server = flask.Flask(__name__)

app = dash.Dash(
    __name__,
    use_pages=True,
    pages_folder=env.ACTIVE_DIR / Path("pages"),
    server=server,
    suppress_callback_exceptions=True,
    assets_ignore=".*ignore.*",
    assets_folder=env.ACTIVE_DIR / Path("assets"),
    external_stylesheets=[
        dbc.themes.CERULEAN,
        dbc.icons.BOOTSTRAP,
        "https://codepen.io/chriddyp/pen/dZVMbK.css",
    ],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

app.layout = html.Div([layout.sidebar(), layout.content])

if env.REDIRECT_POLICY:

    @server.before_request
    def validate_get_request():
        return getattr(redirect, env.REDIRECT_POLICY)()


if __name__ == "__main__":
    app.run(
        host=env.HOST, port=env.PORT, debug=env.DASH_DEBUG, dev_tools_hot_reload=False
    )
