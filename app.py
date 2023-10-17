import dash
import dash_bootstrap_components as dbc
import flask
from dash import html

import layout
from settings import env

server = flask.Flask(__name__)

app = dash.Dash(
    __name__,
    use_pages=True,
    pages_folder="pages",
    server=server,
    suppress_callback_exceptions=True,
    assets_ignore=".*ignore.*",
    assets_folder="assets",
    external_stylesheets=[
        dbc.themes.CERULEAN,
        dbc.icons.BOOTSTRAP,
        "https://codepen.io/chriddyp/pen/dZVMbK.css",
    ],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

app.layout = html.Div([layout.sidebar(), layout.content])


if __name__ == "__main__":
    app.run(
        host=env.HOST, port=env.PORT, debug=env.DASH_DEBUG, dev_tools_hot_reload=False
    )
