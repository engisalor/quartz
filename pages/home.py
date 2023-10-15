import dash
from dash import html

from components.aio.aio import MarkdownFileAIO
from settings import env

dash.register_page(__name__, path="/", title="Quartz")

layout = html.Div(children=[MarkdownFileAIO(env.HOME_MD)])
