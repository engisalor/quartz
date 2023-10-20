# Copyright (c) 2023 Loryn Isaacs
# This file is part of Quartz, licensed under GPL3+ https://github.com/engisalor/quartz
"""Components for the Corpora page."""
import uuid

import plotly.express as px
from dash import MATCH, Input, Output, State, callback, dash_table, dcc, html
from dash.dash_table.Format import Format

from components.aio.aio import MarkdownFileAIO
from settings import corp_data

table_props = {
    "style_table": {"max-height": 181, "max-width": 500, "overflowY": "auto"},
    "style_as_list_view": True,
    "sort_action": "native",
}


def make_columns(cols, override: list = []):
    if override:
        cols = override
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

        sizes = corp_data.sizes.loc[corp_data.sizes["corpus"] == corpus]
        structures = corp_data.structures.loc[corp_data.structures["corpus"] == corpus]
        vals = corp_data.structures.query("corpus==@corpus and exclude==False")
        options = vals.apply(
            lambda row: {"label": row["label"], "value": row["attr"]}, axis=1
        ).to_list()
        options = sorted(options, key=lambda dt: dt["label"])

        super().__init__(
            [
                MarkdownFileAIO(corp_data.dt[corpus].get("md_file")),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H5("Sizes"),
                                dash_table.DataTable(
                                    data=sizes.sort_values(
                                        "size", ascending=False
                                    ).to_dict("records"),
                                    columns=make_columns(
                                        sizes.columns, ["structure", "size"]
                                    ),
                                    **table_props,
                                ),
                            ]
                        ),
                        html.Div(
                            [
                                html.H5("Attributes"),
                                dash_table.DataTable(
                                    data=structures.to_dict("records"),
                                    columns=make_columns(
                                        structures.columns, ["label", "size"]
                                    ),
                                    **table_props,
                                ),
                            ]
                        ),
                        html.Div(
                            [
                                html.H5("Attribute details"),
                                dcc.Dropdown(
                                    clearable=False,
                                    options=options,
                                    value=options[0]["value"],
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
        df = corp_data.ttypes.loc[corp_data.ttypes["corpus"] == corpus]
        slice = df.query("attribute == @attribute")
        fig = px.pie(
            slice,
            values="frq",
            names="str",
            hole=0.3,
            width=320,
            title=f"{len(slice)} most common value(s)",
        )
        fig.update_traces(textposition="inside", textinfo="label")
        fig.update_layout(
            margin=dict(
                l=0,
                r=0,
                t=60,
                b=20,
            ),
            showlegend=False,
            hoverlabel=dict(
                font_size=16,
            ),
        )
        return [
            dcc.Graph(figure=fig),
        ]
