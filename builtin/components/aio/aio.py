"""All-in-one components."""
import pathlib
import uuid

import dash_bootstrap_components as dbc
from dash import MATCH, Input, Output, State, callback, dcc, html

from builtin.utils import io


class MarkdownFileAIO(html.Div):
    """Displays markdown content from a file.

    Args:
        file: Filename with relative path.
        markdown_props: Additional args for dcc.Markdown.
        aio_id: Unique, static ID from the component (optional)."""

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
        markdown_props={"style": {"maxWidth": "800px"}},
        aio_id: str = None,
    ):
        with open(pathlib.Path(file)) as f:
            text = f.read()

        if aio_id is None:
            aio_id = str(uuid.uuid4())

        markdown_props = markdown_props.copy() if markdown_props else {}
        if "children" not in markdown_props:
            markdown_props["children"] = text

        super().__init__([dcc.Markdown(id=self.ids.markdown(aio_id), **markdown_props)])


class CollapsingContentAIO(html.Div):
    """Makes a collapsing content component with associated button."""

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
        Input(ids.dbc_button(MATCH), "n_clicks"),
        State(ids.dbc_collapse(MATCH), "is_open"),
        prevent_initial_callback=True,
    )
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open


class PopoverHeaderAIO(html.Div):
    """Makes a popover header with a title.

    Args:
        header: Text displayed as header.
        file: Relative path to markdown file for title content.
        title: Title content (use either ``file`` or ``title`` arg).
        aio_id: Unique, static ID from the component (optional)."""

    class ids:
        def popoverheader(aio_id):
            return {
                "component": "PopoverHeaderWithMarkdownTitle",
                "subcomponent": "popoverheader",
                "aio_id": aio_id,
            }

    ids = ids

    def __init__(
        self,
        header: str,
        file: str = None,
        title: str = None,
        aio_id: str = None,
    ):
        if aio_id is None:
            aio_id = str(uuid.uuid4())

        if file:
            title = io.load_markdown(file)
        elif title:
            pass
        else:
            raise ValueError("Must supply either `file` or `title` args.")

        super().__init__(
            [
                dbc.PopoverHeader(
                    [
                        html.Div(
                            header,
                            title=title,
                        )
                    ]
                ),
            ]
        )
