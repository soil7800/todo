from .settings import *
from .settings_prod import *


try:
    from .settings_dev import *
except ModuleNotFoundError:
    pass