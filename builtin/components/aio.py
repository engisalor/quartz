import pathlib
import uuid

from dash import dcc, html


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
        markdown_props: dict = None,
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
