import textwrap

import numpy as np
import pandas as pd
import plotly.express as px
from dash import dash_table, dcc, html
from plotly import graph_objects as go

from settings import corp_data


def data_table(data: pd.DataFrame, args_map: list) -> html.Div:
    """Builds a table of summary statistics."""

    df = pd.DataFrame()
    for c in data["corpname"].unique():
        corpus = corp_data.dt[c].get("name")
        for arg in args_map:
            nicearg = arg[1]  # noqa: F841
            slice = data.query("corpname == @c and nicearg == @nicearg")
            fmaxitems = "|".join(slice["fmaxitems"].unique())
            maxitems_note = (
                f"(5 years, 12 themes, etc., up to the {fmaxitems} most common)"
            )
            total_frq = slice["total_frq"].unique()
            if len(total_frq) == 1:
                total_frq = f"{total_frq[0]:,}"
            fpmcorp = slice["total_fpm"].unique()
            if len(fpmcorp) == 1:
                fpmcorp = f"{fpmcorp[0]:,}"
            attr = slice["attribute"].unique()[0]
            record = [
                {
                    "query": arg[0],
                    "cql": " & ".join(slice["arg"].unique()),
                    "corpus": corpus,
                    "attribute": corp_data.dt[c]["label"][attr],
                    "n attr.": f'{slice["value"].count():,}',
                    "frq corp.": total_frq,
                    "frq attr.": f'{slice["frq"].sum():,}',
                    "fpm corp.": fpmcorp,
                    "M rel %": f'{slice["rel"].mean():,.2f}',
                    "M reltt": f'{slice["reltt"].mean():,.2f}',
                    "M fpm": f'{slice["fpm"].mean():,.2f}',
                    "M frq": f'{slice["frq"].mean():,.2f}',
                }
            ]
            df = pd.concat([df, pd.DataFrame.from_records(record)])

    tooltip = {
        "n attr.": f"Number of text types {maxitems_note}",
        "frq corp.": "Occurrences in the whole corpus",
        "frq attr.": "Sum of occurrences in each attribute",
        "fpm corp.": "Frequency per million tokens in the whole corpus",
        "M rel %": "Mean relative density in text types",
        "M reltt": "Mean relative density per million in text types",
        "M fpm": "Mean frequency per million in text types",
        "M frq": "Mean occurrences in text types",
    }

    dt = df.sort_values(["query", "corpus"]).to_dict("records")
    tooltip_data = [
        {
            column: {"value": str(value), "type": "markdown"}
            for column, value in row.items()
        }
        for row in dt
    ]

    return html.Div(
        dash_table.DataTable(
            data=dt,
            columns=[{"id": c, "name": c} for c in df.columns],
            tooltip_header=tooltip,
            tooltip_data=tooltip_data,
            css=[
                {
                    "selector": ".dash-table-tooltip",
                    "rule": "position:fixed; color: black",
                }
            ],
            style_header_conditional=[
                {
                    "if": {"column_id": col},
                    "textDecoration": "underline",
                    "textDecorationStyle": "dotted",
                }
                for col in tooltip
            ]
            + [{"textAlign": "center", "fontWeight": "bold"}],
            style_cell={
                "overflow": "hidden",
                "textOverflow": "ellipsis",
                "maxWidth": 0,
            },
            style_data_conditional=[
                {"if": {"column_id": col}, "textAlign": "left"}
                for col in ["query", "corpus", "attribute"]
            ],
        )
    )


def bar_chart(data: pd.DataFrame, arg_map: list) -> html.Div:
    """Builds bar graphs for given data and query/nicearg."""

    def customize_annotation(annotation):
        attrs = []
        for corpus in data["corpname"].unique():
            for attr in data["attribute"].unique():
                attrs.append(corp_data.dt[corpus]["label"].get(attr, None))
        text = (
            "x="
            + " & ".join(set([x for x in attrs if x]))
            + "\ty="
            + annotation.text.split("=")[-1]
        )
        annotation.update(text=text, font_size=15)

    def make_fig(query, nicearg):
        df = data.query("nicearg == @nicearg").copy()
        df["corpus"] = df["corpname"].replace(
            {k: corp_data.dt[k]["name"] for k in corp_data.dt.keys()}
        )
        df.sort_values(["corpus", "f", "value"], inplace=True)
        df[""] = df["f"]  # patch for removing y axis subplot titles
        df["cql"] = df["arg"].apply(lambda t: "<br>".join(textwrap.wrap(t, 80)))
        df["val"] = df["value"].apply(lambda t: "<br>".join(textwrap.wrap(t, 80)))
        fig = px.bar(
            df,
            x="value",
            y="",
            color="corpus",
            barmode="group",
            facet_col="statistic",
            facet_col_wrap=1,
            facet_row_spacing=0.1,
            height=len(df["statistic"].unique()) * 150 + 180,
            hover_data={
                "corpus": False,
                "corpname": False,
                "nicearg": False,
                "value": False,
                "": False,
                "f": ":.2f",
                "statistic": False,
            },
            category_orders={
                "corpname": sorted(df["corpname"].unique()),
                "statistic": sorted(df["statistic"].unique()),
            },
        )
        fig.update_layout(
            hovermode="x unified",
            plot_bgcolor="#ffffff",
            title=dict(text=query, font=dict(size=22), yref="container"),
            xaxis_title="",
            yaxis_title="",
            xaxis={"categoryorder": "category ascending"},
        )
        fig.update_yaxes(matches=None)
        fig.update_xaxes(automargin=False)
        fig.for_each_annotation(customize_annotation)
        return fig

    return html.Div(
        [html.Div(dcc.Graph(figure=make_fig(arg[0], arg[1]))) for arg in arg_map]
    )


def choropleth(data: pd.DataFrame, arg_map: list) -> html.Div:
    graphs = []
    for arg in arg_map:
        nicearg = arg[1]  # noqa: F841
        _data = data.query("nicearg == @nicearg").copy()
        attribute = "/".join(_data["attribute"].unique())
        _data["value"] = _data["value"].copy().str.upper()
        print("STATS", sorted(_data["statistic"].unique()))
        for stat in sorted(_data["statistic"].unique()):
            slice = _data.loc[_data["statistic"] == stat]
            if stat == "frq":
                slice["_f"] = slice["f"].apply(np.log10).round(2)
                title = f"log10<br>{stat}"
            else:
                slice["_f"] = slice["f"].round(2)
                title = stat
            for c in sorted(slice["corpname"].unique()):
                df = slice.loc[
                    (slice["corpname"] == c) & (~slice["value"].str.contains(r"\|"))
                ].copy()
                df["text"] = ""
                if stat == "frq":
                    df["text"] += f"{stat}=" + df["f"].astype(int).astype(str)
                # annotations
                anno_0 = f'Mean of {len(df)} values = {round(df["_f"].mean(), 2):,}'
                wld = df.loc[df["value"] == "WLD", "_f"].sum().round(2)
                if len(df.loc[df["value"] == "WLD"]) > 1:
                    raise ValueError("more than one WLD row found")
                elif wld:
                    anno_1 = f"World = {wld}"
                else:
                    anno_1 = ""
                footer = (
                    f'{corp_data.dt[c]["name"]}\t{corp_data.dt[c]["label"][attribute]}'
                    + f"<br>{anno_0}\t{anno_1}"
                )
                # create figure
                fig = go.Figure(
                    data=go.Choropleth(
                        locations=df["value"],
                        z=df["_f"],
                        text=df["text"],
                        colorbar=dict(
                            orientation="v",
                            title=title,
                        ),
                    ),
                )
                fig.update_layout(
                    autosize=True,
                    title=dict(text=arg[0], font=dict(size=22), yref="container"),
                    geo=dict(
                        showframe=False,
                        showcoastlines=False,
                        projection_type="cylindrical equal area",
                    ),
                    height=500,
                    font_size=15,
                    annotations=[
                        dict(x=0.5, y=0, showarrow=False, text=footer),
                    ],
                )
                graphs.append(fig)

    return [html.Div(dcc.Graph(figure=x, config=dict(responsive=True))) for x in graphs]
