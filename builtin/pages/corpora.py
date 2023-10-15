from pathlib import Path

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, get_app, html

from builtin.components.aio.aio import MarkdownFileAIO
from builtin.components.aio.corpora import CorpusDetailsAIO
from environment.settings import corp_data, env

app = get_app()


dash.register_page(__name__)


layout = html.Div(
    [
        MarkdownFileAIO(env.ACTIVE_DIR / Path("markdown/corpora.md")),
        html.Br(),
        dbc.Tabs(
            [
                dbc.Tab(
                    label=corp_data.dt[corpus]["name"],
                    tab_id=corpus,
                )
                for corpus in [k for k in corp_data.dt.keys()]
            ],
            id="tabs",
        ),
        html.Div(id="content"),
    ]
)


@dash.callback(Output("content", "children"), Input("tabs", "active_tab"))
def switch_tab(corpus):
    return CorpusDetailsAIO(corpus)
