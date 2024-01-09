# Copyright (c) 2023 Loryn Isaacs
# This file is part of Quartz, licensed under GPL3+ https://github.com/engisalor/quartz
import json
import textwrap
import uuid

import dash_bootstrap_components as dbc
import pandas as pd
from dash import MATCH, Input, Output, State, callback, ctx, dcc, html
from sgex.job import Job
from sgex.query import _query_escape

from components.freqs_fig import bar_figure, prep_data
from settings import corp_data, env
from utils import url


def _update_link(point: dict) -> dbc.NavLink:
    """Generates a nav link based on figure click data."""
    ls = point.get("customdata")
    params = json.loads(ls[0])
    href = url.cql_ttype_filter(
        params=params,
        attr_path=ls[1],
        value=ls[2],
        base_url=env.SERVER_URL.rstrip("/") + "/#concordance?",
    )
    return dbc.NavLink(
        html.I(
            className="bi bi-arrow-up-right-square-fill",
            title="Go to " + corp_data.dt[params["corpname"]]["name"],
            style={"color": corp_data.dt[params["corpname"]]["color"]},
        ),
        href=href,
        target="_blank",
    )


def _params_from_point(
    point: dict, crossfilter, crossfilter_sorting, crossfilter_page
) -> tuple:
    """Builds API parameters from figure click data point."""
    params, attr_path, value = point.get("customdata", [None] * 3)[:3]
    params = json.loads(params)
    corpus = params["corpname"]
    label_map = {v: k for k, v in corp_data.dt[corpus]["label"].items()}
    struct, attr = url.split_attr_path(attr_path)
    params["call_type"] = "Freqs"
    params["q"] += f' within <{struct} {attr}="{_query_escape(value)}" />'
    params["fcrit"] = f"{label_map[crossfilter]} 0"
    params["freq_sort"] = crossfilter_sorting
    params["fpage"] = crossfilter_page
    # also try: [f"{x} 0" for x in corp_data.dt[_params["corpname"]]["label"].keys()]
    x_suffix = corp_data.dt[corpus]["label"][attr_path] + f"=`{value}`"
    return params, x_suffix


def _df_from_crossfilter(
    clickdata: dict, crossfilter, title, crossfilter_sorting, crossfilter_page
) -> tuple:
    """Runs API calls based on figure click data."""
    params = []
    for point in clickdata["points"]:
        _params, x_suffix = _params_from_point(
            point, crossfilter, crossfilter_sorting, crossfilter_page
        )
        params.append(_params)
    j = Job(params=params, **env.sgex)
    j.run()
    dfs = []
    for call in j.data.freqs:
        df = call.df_from_json()
        df["params"] = json.dumps(call.params)
        df["query"] = title
        dfs.append(df)
    return pd.concat(dfs), x_suffix


def _pop_attr_annotation(annotation):
    if annotation.text.startswith("attr"):
        annotation.update(text="")


class SkeGraphAIO(html.Div):
    class ids:
        title = lambda aio_id: {  # noqa: E731
            "type": "Title",
            "group": aio_id,
        }
        link1 = lambda aio_id: {  # noqa: E731
            "type": "Link1",
            "group": aio_id,
        }
        link2 = lambda aio_id: {  # noqa: E731
            "type": "Link2",
            "group": aio_id,
        }
        graph1 = lambda aio_id: {  # noqa: E731
            "type": "Graph1",
            "group": aio_id,
        }
        graph2 = lambda aio_id: {  # noqa: E731
            "type": "Graph2",
            "group": aio_id,
        }
        graph1_div = lambda aio_id: {  # noqa: E731
            "type": "Graph1_div",
            "group": aio_id,
        }
        graph2_div = lambda aio_id: {  # noqa: E731
            "type": "Graph2_div",
            "group": aio_id,
        }

    ids = ids

    def __init__(
        self,
        title: str,
        aio_id=None,
        **kwargs,
    ):
        if aio_id is None:
            aio_id = str(uuid.uuid4())

        title_div = html.Div(
            children=[
                html.H3(title, style={"margin-bottom": "0px"}),
                dcc.Store(id=self.ids.title(aio_id), data=title),
            ],
            className="title-div",
        )

        text = ""
        for annotation in kwargs["figure"].layout.annotations:
            if annotation.text.startswith("attr"):
                text += annotation.text
        text = "<br>".join(textwrap.wrap(text, 80))
        kwargs["figure"].for_each_annotation(_pop_attr_annotation)

        graph1_div = html.Div(
            children=[
                html.Div(
                    html.I(
                        className="bi bi-arrow-up-right-square-fill",
                        title="Select a data point",
                    ),
                    id=self.ids.link1(aio_id),
                    className="link-div",
                ),
                dcc.Markdown(text),
                dcc.Graph(id=self.ids.graph1(aio_id), **kwargs),
            ],
            id=self.ids.graph1_div(aio_id),
            className="graph-div",
        )

        graph2_div = html.Div(
            html.P("Crossfilter disabled", className="lead"),
            id=self.ids.graph2_div(aio_id),
            className="graph-div",
        )

        super().__init__(
            [
                title_div,
                graph1_div,
                graph2_div,
            ],
            className="graph-group",
        )

    @callback(
        Output(ids.link1(MATCH), "children"),
        Input(ids.graph1(MATCH), "clickData"),
        prevent_initial_call=True,
    )
    def update_link1(clickData):
        if clickData:
            _links1 = [_update_link(point) for point in clickData["points"]]
            return sorted(_links1, key=lambda nav: nav.href)

    @callback(
        Output(ids.link2(MATCH), "children"),
        Input(ids.graph2(MATCH), "clickData"),
        prevent_initial_call=True,
    )
    def update_link(clickData):
        if clickData:
            _links1 = [_update_link(point) for point in clickData["points"]]
            return sorted(_links1, key=lambda nav: nav.href)

    @callback(
        Output(ids.graph2_div(MATCH), "children"),
        Input(ids.graph1(MATCH), "clickData"),
        Input("crossfilter-picker", "value"),
        Input(ids.title(MATCH), "data"),
        Input("crossfilter-sort-picker", "value"),
        Input("crossfilter-page-picker", "value"),
        State("corpora-picker", "value"),
        State("attribute-picker", "value"),
        State("statistic-picker", "value"),
        State("sort-picker", "value"),
    )
    def make_graph2(
        clickdata,
        crossfilter,
        title,
        crossfilter_sorting,
        crossfilter_page,
        corpora,
        attribute,
        statistics,
        sort,
    ):
        id = ctx.outputs_list["id"] | {"type": "Graph2"}
        if not crossfilter:
            return html.P("Crossfilter disabled", className="lead")
        if not clickdata:
            return html.P("Select a data point to crossfilter", className="lead")

        df, x_suffix = _df_from_crossfilter(
            clickdata, crossfilter, title, crossfilter_sorting, crossfilter_page
        )
        if df.empty:
            return html.P("Nothing found", className="lead")

        df = prep_data(
            corpora,
            crossfilter,
            [],
            statistics,
            crossfilter_sorting,
            crossfilter_page,
            df,
        )
        fig = bar_figure(df)
        text = ""
        for annotation in fig.layout.annotations:
            if annotation.text.startswith("attr"):
                text += f"{x_suffix} {annotation.text}"
        fig.for_each_annotation(_pop_attr_annotation)
        return [
            html.Div(
                html.I(
                    className="bi bi-arrow-up-right-square-fill",
                    title="No data point selected",
                ),
                id=id | {"type": "Link2"},
                className="link-div",
            ),
            dcc.Markdown(text),
            dcc.Graph(figure=fig, id=id | {"type": "Graph2"}),
        ]
