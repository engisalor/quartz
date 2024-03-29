import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, get_app, html

from components.aio.aio import MarkdownFileAIO
from components.aio.corpora import CorpusDetailsAIO
from settings import corp_data, env

app = get_app()


dash.register_page(__name__)

text_file = getattr(env, "CORPORA_MD", None)
if not text_file:
    main_text = html.Div(html.H2("Corpora"))
else:
    main_text = MarkdownFileAIO(text_file)

layout = html.Div(
    [
        main_text,
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
