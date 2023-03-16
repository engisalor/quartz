import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, get_app, html

import environment.settings as env
from builtin.components.aio.aio import MarkdownFileAIO
from builtin.components.aio.corpora import CorpusDetailsAIO

app = get_app()


dash.register_page(__name__)


layout = html.Div(
    [
        MarkdownFileAIO("builtin/markdown/corpora.md"),
        html.Br(),
        dbc.Tabs(
            [
                dbc.Tab(
                    label=env.corpora[corpus]["name"],
                    tab_id=corpus,
                )
                for corpus in [k for k in env.corpora.keys()]
            ],
            id="tabs",
        ),
        html.Div(id="content"),
    ]
)


@dash.callback(Output("content", "children"), Input("tabs", "active_tab"))
def switch_tab(corpus):
    return CorpusDetailsAIO(corpus)
