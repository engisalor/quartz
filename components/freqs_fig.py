# Copyright (c) 2023 Loryn Isaacs
# This file is part of Quartz, licensed under GPL3+ https://github.com/engisalor/quartz
import textwrap

import pandas as pd
import plotly.express as px
from dash import dash_table, html

from settings import corp_data, env, stats


def prep_data(
    corpora, attribute, attribute_filter, statistics, sort, page, df: pd.DataFrame
):
    """Prepares frequency data from API calls for drawing figures."""
    # filtering
    query_args = []
    if len(corpora):
        query_args.append("corpname in @corpora")
    _df = corp_data.structures
    attrs = _df.loc[  # noqa: F841
        (_df["corpus"].isin(corpora)) & (_df["label"] == attribute), "attr"
    ].to_list()
    query_args.append("attribute in @attrs")
    if len(attribute_filter):
        query_args.append("value in @attribute_filter")
    if len(query_args):
        slice = df.query(" and ".join(query_args)).copy()
    else:
        slice = df.copy()
    # melting statistics
    melted_slice = slice.melt(
        id_vars=[x for x in slice.columns if x not in stats.keys()],
        var_name="statistic",
        value_name="f",
    )
    melted_slice.query("statistic in @statistics", inplace=True)
    melted_slice.sort_values("value", inplace=True)
    melted_slice["sort"] = sort
    melted_slice["page"] = page
    return melted_slice


def bar_figure(data: pd.DataFrame, arg=None) -> px.bar:
    """Builds a bar chart. Use `arg` to filter data for the desired query."""
    if arg:
        df = data.query("arg == @arg").copy()
    else:
        df = data.copy()
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
        color_discrete_map=corp_data.colors,
        barmode="group",
        facet_col="statistic",
        facet_col_wrap=1,
        facet_row_spacing=0.07,
        custom_data=["params", "attribute", "value"],
        height=len(df["statistic"].unique()) * 150 + 150,
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
        margin=dict(l=0, r=0, t=20),
        xaxis_title="",
        # yaxis_title="",
        xaxis={"categoryorder": "category ascending"},
    )
    fig.update_yaxes(matches=None)
    fig.update_xaxes(automargin=False)

    attrs = []
    for corpus in data["corpname"].unique():
        for attr in data["attribute"].unique():
            attrs.append(corp_data.dt[corpus]["label"].get(attr, None))

    def bar_annotation(annotation, attrs=attrs):
        "Abbreviates the default bar `statistics` annotation."
        text = "stat=" + annotation.text.split("=")[-1]
        annotation.update(text=text, font_size=15)

    fig.for_each_annotation(bar_annotation)

    text = f'attr=`{"&".join(set([x for x in attrs if x]))}`'
    text += f' sort=`{"&".join(df["sort"].unique())}`'
    text += f' page=`{"&".join(df["page"].unique().astype(str))}`'
    text = "<br>".join(textwrap.wrap(text, 80))

    fig.add_annotation(
        xref="paper",
        yref="paper",
        x=0.5,
        font_size=15,
        showarrow=False,
        text=text,
    )
    return fig


def choropleth_figure(
    df: pd.DataFrame, corpus, stat, attribute, hover_data
) -> px.choropleth:
    """Builds a choropleth figure based on input variables."""
    # annotations
    sort = "&".join(df["sort"].unique())
    page = "&".join(df["page"].unique().astype(str))
    anno_0 = f"mean={round(df[stat].mean(), 2):,} (of {len(df)})"
    anno_2 = f"sort={sort} page={page}"
    wld = df.loc[df["iso3"] == "WLD", stat].sum().round(2)
    if len(df.loc[df["iso3"] == "WLD"]) > 1:
        raise ValueError("more than one WLD row found")
    elif wld:
        anno_1 = f"World={wld}"
        if "frq" in df["statistic"].values:
            frq = df.loc[df["iso3"] == "WLD", "frq"].sum()
            anno_1 = f"World frq_log10={wld} frq={frq}"
    else:
        anno_1 = ""
    footer = (
        f'{corp_data.dt[corpus]["name"]}\t{corp_data.dt[corpus]["label"][attribute]}'
        + f"<br>{anno_1}<br>{anno_0}<br>{anno_2}"
    )
    # create figure
    fig = px.choropleth(
        df,
        locations="iso3",
        color=stat,
        custom_data=["params", "attribute", "value"],
        hover_data=hover_data,
    )
    fig.update_layout(
        autosize=True,
        margin=dict(l=0, r=0, t=0, b=0),
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type="cylindrical equal area",
        ),
        height=300,
        font_size=15,
        annotations=[
            dict(x=0.5, y=0.01, showarrow=False, text=footer),
        ],
    )
    return fig


def data_table(data: pd.DataFrame, sort, page) -> html.Div:
    """Builds a table of summary statistics."""

    def make_record(c, arg):
        df = data.query("corpname == @c and arg == @arg")
        if not df.empty:
            attr = " & ".join(df["attribute"].unique())
            return {
                "query": " & ".join(df["query"].unique()),
                "cql": " & ".join(df["arg"].unique()),
                "corpus": corp_data.dt[c].get("name"),
                "attribute": corp_data.dt[c]["label"][attr],
                "n attr.": f'{df["value"].count():,}',
                "sort": sort,
                "page": page,
                "frq corp.": " & ".join([f"{x:,}" for x in df["total_frq"].unique()]),
                "frq attr.": f'{df["frq"].sum():,}',
                "fpm corp.": " & ".join([f"{x:,}" for x in df["total_fpm"].unique()]),
                "M rel %": f'{df["rel"].mean():,.2f}',
                "M reltt": f'{df["reltt"].mean():,.2f}',
                "M fpm": f'{df["fpm"].mean():,.2f}',
                "M frq": f'{df["frq"].mean():,.2f}',
            }

    records = []
    for arg in sorted(data["arg"].unique()):
        for c in sorted(data["corpname"].unique()):
            records.append(make_record(c, arg))
    records = [x for x in records if x]

    tooltip = {
        "n attr.": f"Number of text types (up to the {env.MAX_ITEMS} most common)",
        "sort": "Frequency sort method",
        "page": "Current page",
        "frq corp.": "Occurrences in the whole corpus",
        "frq attr.": "Sum of occurrences in each attribute",
        "fpm corp.": "Frequency per million tokens in the whole corpus",
        "M rel %": "Mean relative density in text types",
        "M reltt": "Mean relative density per million in text types",
        "M fpm": "Mean frequency per million in text types",
        "M frq": "Mean occurrences in text types",
    }

    tooltip_data = [
        {
            column: {"value": str(value), "type": "markdown"}
            for column, value in row.items()
        }
        for row in records
    ]

    return html.Div(
        dash_table.DataTable(
            data=records,
            columns=[{"id": c, "name": c} for c in records[0].keys()],
            tooltip_header=tooltip,
            tooltip_data=tooltip_data,
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
