import importlib

import dash
import dash_bootstrap_components as dbc
import flask
from dash import CeleryManager, DiskcacheManager, html

import environment.settings as env

if env.cache_config.get("CACHE_REDIS_HOST"):
    host = env.cache_config.get("CACHE_REDIS_HOST")
    from celery import Celery

    celery_app = Celery(__name__, broker=host, backend=host)
    background_callback_manager = CeleryManager(celery_app)
else:
    import diskcache

    cache = diskcache.Cache(".cache")
    background_callback_manager = DiskcacheManager(cache)


layout = importlib.import_module(env.LAYOUT_MODULE)
server = flask.Flask(__name__)

app = dash.Dash(
    __name__,
    use_pages=True,
    background_callback_manager=background_callback_manager,
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
    app.run(
        host=env.HOST, port=env.PORT, debug=env.DASH_DEBUG, dev_tools_hot_reload=False
    )
