import os
from fastapi.templating import Jinja2Templates

from app.services.media import media_url

templates = Jinja2Templates(directory="app/pages")

_version_file = "version.txt"
if os.path.exists(_version_file):
    with open(_version_file) as _f:
        _version = _f.read().strip()
else:
    _version = "dev"

templates.env.globals["app_version"] = _version
templates.env.globals["media_url"] = media_url
