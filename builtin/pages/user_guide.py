import dash

from builtin.components.aio.aio import MarkdownFileAIO

dash.register_page(__name__)


layout = MarkdownFileAIO("builtin/markdown/user_guide.md")
