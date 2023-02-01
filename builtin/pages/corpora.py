import dash
from dash import html

from builtin.components.aio.corpora import CorpusOverviewAIO
from environment.settings import corpora

dash.register_page(__name__)


layout = html.Div(
    [
        html.H1("Corpora"),
        html.P(
            "Descriptions for corpora are generated with API calls and Markdown files.",
            style={"max-width": "800px"},
        ),
        html.Div([CorpusOverviewAIO(corpus) for corpus in corpora]),
    ]
)
