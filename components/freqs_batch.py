# Copyright (c) 2023 Loryn Isaacs
# This file is part of Quartz, licensed under GPL3+ https://github.com/engisalor/quartz
import numpy as np
import pandas as pd
from dash import html

from components.aio.ske_graph import SkeGraphAIO
from components.freqs_fig import bar_figure, choropleth_figure


def bar_batch(data: pd.DataFrame) -> html.Div:
    """Builds a batch of bar graphs."""
    queries = data.drop_duplicates(["query", "arg"])
    return [
        SkeGraphAIO(
            title=row["query"],
            figure=bar_figure(data, row["arg"]),
        )
        for _, row in queries.sort_values("arg").iterrows()
    ]


def choropleth_batch(data: pd.DataFrame) -> html.Div:
    """Builds a batch of choropleth figures."""
    graphs = []
    for arg in sorted(data["arg"].unique()):
        _data = data.query("arg == @arg").copy()
        attribute = "/".join(_data["attribute"].unique())
        _data["iso3"] = _data["value"].str.upper()
        for stat in sorted(_data["statistic"].unique()):
            slice = _data.loc[_data["statistic"] == stat].copy()
            if stat == "frq":
                stat = f"{stat}_log10"
                slice[stat] = slice["f"].apply(np.log10).round(2)
                slice["frq"] = slice["f"].apply(lambda x: f"{int(x):,}")
                hover_data = [stat, "frq", "iso3"]
            else:
                slice[stat] = slice["f"].round(2)
                hover_data = [stat, "iso3"]
            for c in sorted(slice["corpname"].unique()):
                df = slice.loc[
                    (slice["corpname"] == c) & (~slice["iso3"].str.contains(r"\|"))
                ].copy()
                fig = choropleth_figure(df, c, stat, attribute, hover_data)
                graphs.append(
                    SkeGraphAIO(
                        title="&".join(df["query"].unique()),
                        figure=fig,
                        config=dict(responsive=True),
                    )
                )

    return graphs
