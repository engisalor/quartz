import importlib

import dash
import dash_bootstrap_components as dbc
import flask
from dash import html

import environment.settings as env



layout = importlib.import_module(env.LAYOUT_MODULE)
server = flask.Flask(__name__)

app = dash.Dash(
    __name__,
    use_pages=True,
    pages_folder=env.PAGES_DIR,
    server=server,
    suppress_callback_exceptions=True,
    assets_ignore=".*ignore.*",
    assets_folder=env.ASSETS_DIR,
    external_stylesheets=[
        dbc.themes.CERULEAN,
        dbc.icons.FONT_AWESOME,
        "https://codepen.io/chriddyp/pen/dZVMbK.css",
    ],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

app.layout = html.Div([layout.sidebar(), layout.content])


if __name__ == "__main__":
    app.run(host=env.HOST, port=env.PORT, debug=env.DASH_DEBUG, dev_tools_hot_reload=False)
