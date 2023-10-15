import dash

from components.aio.aio import MarkdownFileAIO
from settings import env

dash.register_page(__name__)


layout = MarkdownFileAIO(env.GUIDE_MD)
