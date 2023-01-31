import dash
from dash import html

from builtin.components.aio import MarkdownFileAIO

dash.register_page(__name__, path="/", title="Quartz")

layout = html.Div(children=[MarkdownFileAIO("home", "builtin/markdown")])
