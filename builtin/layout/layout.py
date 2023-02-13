import dash
import dash_bootstrap_components as dbc
from dash import html


def sidebar():
    sidebar_contents = [
        dbc.NavLink(
            [html.Span(page["name"])], href=page["relative_path"], active="exact"
        )
        for page in dash.page_registry.values()
    ]

    return html.Div(
        [
            html.Div(
                html.A(
                    html.Img(src="assets/sidebar-icon.png", className="sidebar-icon"),
                    href="/",
                )
            ),
            html.Div(html.P("Quartz", className="lead"), className="sidebar-header"),
            html.Div(html.I(className="bi bi-list"), className="sidebar-bars"),
            dbc.Nav(
                sidebar_contents,
                vertical=True,
                pills=True,
            ),
        ],
        className="sidebar",
    )


content = html.Div(dash.page_container, id="page-content")
