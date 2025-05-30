from flask import Blueprint

router = Blueprint("router", __name__)

from routes.home import *
from routes.api_status import *
from routes.upload import *
from routes.ask import *
from routes.view_text import *
from routes.error import *
