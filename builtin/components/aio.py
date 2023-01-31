import pathlib
import uuid

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import MATCH, Input, Output, State, callback, dcc, html

from builtin.call import parse


class MarkdownFileAIO(html.Div):
    class ids:
        def markdown(aio_id):
            return {
                "component": "MarkdownFileAIO",
                "subcomponent": "markdown",
                "aio_id": aio_id,
            }

    ids = ids

    def __init__(
        self,
        file: str,
        dir: str = "markdown",
        markdown_props={"style": {"max-width": "800px"}},
        aio_id: str = None,
    ):
        """Displays markdown content from a file.

        Args:
            file: Filename with or without an ``.md`` extension.
            dir: Relative path to file.
            markdown_props: Additional args for dcc.Markdown.
            aio_id: Unique, static ID from the component (optional)."""

        with open(dir / pathlib.Path(file).with_suffix(".md")) as f:
            text = f.read()

        if aio_id is None:
            aio_id = str(uuid.uuid4())

        markdown_props = markdown_props.copy() if markdown_props else {}
        if "children" not in markdown_props:
            markdown_props["children"] = text

        super().__init__([dcc.Markdown(id=self.ids.markdown(aio_id), **markdown_props)])


class CollapsingContentAIO(html.Div):
    class ids:
        def dbc_button(aio_id):
            return {
                "component": "CollapsableAreaAIO",
                "subcomponent": "dbc_button",
                "aio_id": aio_id,
            }

        def dbc_collapse(aio_id):
            return {
                "component": "CollapsableAreaAIO",
                "subcomponent": "dbc_collapse",
                "aio_id": aio_id,
            }

    ids = ids

    def __init__(
        self,
        button_text: str,
        content: list,
        dbc_button_props={
            "color": "light",
            "n_clicks": 0,
            "className": "mb-3",
        },
        dbc_collapse_props={"is_open": False},
        aio_id: str = None,
    ):
        """A collapsing content component with button toggle."""

        if aio_id is None:
            aio_id = str(uuid.uuid4())

        super().__init__(
            [
                dbc.Button(
                    button_text, id=self.ids.dbc_button(aio_id), **dbc_button_props
                ),
                dbc.Collapse(
                    content, id=self.ids.dbc_collapse(aio_id), **dbc_collapse_props
                ),
            ]
        )

    @callback(
        Output(ids.dbc_collapse(MATCH), "is_open"),
        [Input(ids.dbc_button(MATCH), "n_clicks")],
        [State(ids.dbc_collapse(MATCH), "is_open")],
    )
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open


class CorpusDetailsAIO(html.Div):
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
        meta,
        aio_id: str = None,
    ):

        if aio_id is None:
            aio_id = str(uuid.uuid4())

        super().__init__(
            [
                html.H3("Details"),
                html.Div(meta, id=self.ids.store(aio_id), hidden=True),
                dcc.Dropdown(
                    clearable=False,
                    id=self.ids.dropdown(aio_id),
                ),
                dcc.Graph(id=self.ids.graph(aio_id)),
            ]
        )

    @callback(
        Output(ids.dropdown(MATCH), "options"),
        Output(ids.dropdown(MATCH), "value"),
        Input(ids.store(MATCH), "children"),
    )
    def attribute_chart(meta):
        wordlist = parse.Wordlist(f"ttype_analysis {meta}")
        attrs = []
        for attr in wordlist.df["attribute"].unique():
            n_unique = len(wordlist.df.query("attribute == @attr"))
            if n_unique >= 2:
                attrs.append(attr)
        attrs = sorted(attrs)
        return attrs, attrs[0]

    @callback(
        Output(ids.graph(MATCH), "figure"),
        Input(ids.dropdown(MATCH), "value"),
        State(ids.store(MATCH), "children"),
    )
    def generate_chart(attribute, meta):
        wordlist = parse.Wordlist(f"ttype_analysis {meta}")
        df = wordlist.df.query("attribute == @attribute")
        fig = px.pie(
            df, values="frq", names="str", hole=0.3, title=f"Top {len(df)} values"
        )
        fig.update_traces(textposition="inside")
        fig.update_layout(uniformtext_minsize=12, uniformtext_mode="hide")
        fig.update_traces(hoverinfo="all")
        return fig


class CorpusOverviewAIO(html.Div):
    class ids:
        def dbc_table_sizes(aio_id):
            return {
                "component": "CorpusOverviewAIO",
                "subcomponent": "dbc_table_sizes",
                "aio_id": aio_id,
            }

        def dbc_table_attributes(aio_id):
            return {
                "component": "CorpusOverviewAIO",
                "subcomponent": "dbc_table_attributes",
                "aio_id": aio_id,
            }

    ids = ids

    def __init__(
        self,
        info: parse.Corp_Info,
        dbc_table_sizes_props={
            "striped": True,
            "bordered": True,
            "style": {"max-width": "200px"},
        },
        dbc_table_attributes_props={
            "striped": True,
            "bordered": True,
            "style": {"max-width": "400px"},
        },
        aio_id: str = None,
    ):

        if aio_id is None:
            aio_id = str(uuid.uuid4())

        info.df["size"] = info.df["size"].apply(lambda x: f"{x:,}")
        sizes = pd.DataFrame(
            {
                "structure": [
                    k.replace("count", "") for k in info.json["sizes"].keys()
                ],
                "size": [f"{int(v):,}" for v in info.json["sizes"].values()],
            }
        )

        super().__init__(
            [
                MarkdownFileAIO(info.meta),
                html.H3("Sizes"),
                dbc.Table.from_dataframe(
                    sizes.sort_values("size", ascending=False),
                    id=self.ids.dbc_table_sizes(aio_id),
                    **dbc_table_sizes_props,
                ),
                html.H3("Attributes"),
                dbc.Table.from_dataframe(
                    info.df,
                    id=self.ids.dbc_table_attributes(aio_id),
                    **dbc_table_attributes_props,
                ),
                CorpusDetailsAIO(info.meta),
            ]
        )
