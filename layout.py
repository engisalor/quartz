import dash
import dash_bootstrap_components as dbc
from dash import html

from version import version


def sidebar():
    # manual sidebar contents
    sidebar_contents = [
        dbc.NavLink(
            [html.I(className="bi bi-search"), html.Span("Query")],
            href="/",
            active="exact",
        ),
        dbc.NavLink(
            [html.I(className="bi bi-database"), html.Span("Corpora")],
            href="/corpora",
            active="exact",
        ),
        dbc.NavLink(
            [html.I(className="bi bi-question-square"), html.Span("User guide")],
            href="/user-guide",
            active="exact",
        ),
    ]

    # automatic sidebar contents
    # sidebar_contents = [
    #     dbc.NavLink(
    #         [html.Span(page["name"])], href=page["relative_path"], active="exact"
    #     )
    #     for page in dash.page_registry.values()
    # ]

    version_tag = html.Small(f"v{version}")
    source_code = dbc.NavLink(
        [html.Span([html.I(className="bi bi-github"), version_tag])],
        href="https://github.com/engisalor/quartz",
        active="exact",
    )

    sidebar_footer = [source_code]

    return html.Div(
        [
            html.Div(
                html.A(
                    html.Img(src="assets/sidebar-icon.png", className="sidebar-icon"),
                    href="/",
                )
            ),
            html.Div(html.P("Quartz", className="lead"), className="sidebar-header"),
            dbc.Nav(
                sidebar_contents,
                vertical=True,
                pills=True,
                className="sidebar-content",
            ),
            dbc.Nav(
                sidebar_footer,
                vertical=True,
                pills=True,
                className="sidebar-footer",
            ),
        ],
        className="sidebar",
    )


content = html.Div(dash.page_container, id="page-content")
