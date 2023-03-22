"""Components for the Corpora page."""
import uuid

import plotly.express as px
from dash import MATCH, Input, Output, State, callback, dash_table, dcc, html
from dash.dash_table.Format import Format

import environment.settings as env
from builtin.components.aio.aio import MarkdownFileAIO

table_props = {
    "style_table": {"max-height": 181, "max-width": 500, "overflowY": "auto"},
    "style_as_list_view": True,
    "sort_action": "native",
}


def make_columns(cols):
    return [
        dict(id=c, name=c, type="numeric", format=Format().group(True)) for c in cols
    ]


class CorpusDetailsAIO(html.Div):
    """Makes a pie chart describing corpus attributes."""

    class ids:
        def store(aio_id):
            return {
                "component": "CorpusDetailsAIO",
                "subcomponent": "store",
                "aio_id": aio_id,
            }

        def dropdown(aio_id):
            return {
                "component": "CorpusDetailsAIO",
                "subcomponent": "dropdown",
                "aio_id": aio_id,
            }

        def graph(aio_id):
            return {
                "component": "CorpusDetailsAIO",
                "subcomponent": "graph",
                "aio_id": aio_id,
            }

    ids = ids

    def __init__(
        self,
        corpus,
        aio_id: str = None,
    ):
        if aio_id is None:
            aio_id = str(uuid.uuid4())

        # get premade calls
        sizes = env.premade_calls[corpus]["sizes_df"]
        structures = env.premade_calls[corpus]["structures_df"]
        attrs = sorted(env.premade_calls[corpus]["attributes_ls"])

        super().__init__(
            [
                MarkdownFileAIO(env.corpora[corpus].get("md_file")),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H5("Sizes"),
                                dash_table.DataTable(
                                    data=sizes.sort_values(
                                        "size", ascending=False
                                    ).to_dict("records"),
                                    columns=make_columns(sizes.columns),
                                    **table_props,
                                ),
                            ]
                        ),
                        html.Div(
                            [
                                html.H5("Attributes"),
                                dash_table.DataTable(
                                    data=structures.to_dict("records"),
                                    columns=make_columns(structures.columns),
                                    **table_props,
                                ),
                            ]
                        ),
                        html.Div(
                            [
                                html.H5("Attribute details"),
                                dcc.Dropdown(
                                    clearable=False,
                                    options=attrs,
                                    value=attrs[0],
                                    id=self.ids.dropdown(aio_id),
                                ),
                            ],
                            style={"width": "300px"},
                        ),
                        dcc.Store(data=corpus, id=self.ids.store(aio_id)),
                        html.Div(id=self.ids.graph(aio_id)),
                    ],
                    style={
                        "display": "inline-flex",
                        "flexWrap": "wrap",
                        "columnGap": "50px",
                    },
                ),
            ]
        )

    @callback(
        Output(ids.graph(MATCH), "children"),
        Input(ids.dropdown(MATCH), "value"),
        State(ids.store(MATCH), "data"),
    )
    def generate_chart(attribute, corpus):
        df = env.premade_calls[corpus]["ttypes_df"].copy()
        slice = df.query("attribute == @attribute")
        fig = px.pie(
            slice,
            values="frq",
            names="str",
            hole=0.3,
            height=500,
            width=500,
            title=f"{len(slice)} most common value(s)",
        )
        fig.update_traces(textposition="inside", textinfo="label")
        fig.update_layout(
            showlegend=False,
            hoverlabel=dict(
                font_size=16,
            ),
        )
        return [
            dcc.Graph(figure=fig),
        ]
