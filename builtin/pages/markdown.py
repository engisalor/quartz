import dash
from dash import html

from builtin.components.aio.aio import MarkdownFileAIO

dash.register_page(__name__)

layout = html.Div(children=[MarkdownFileAIO("cheatsheet", "builtin/markdown")])
