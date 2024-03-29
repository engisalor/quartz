import dash

from components.aio.aio import MarkdownFileAIO
from settings import env

dash.register_page(__name__)


layout = MarkdownFileAIO(getattr(env, "GUIDE_MD", None))
