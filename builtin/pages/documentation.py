import dash
from dash import dcc, html

from builtin.utils.io import compile_markdown

dash.register_page(__name__)


text = compile_markdown("builtin/markdown/documentation")
layout = html.Div(children=[dcc.Markdown(text, style={"max-width": "800px"})])
