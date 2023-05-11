# flake8: noqa F401
import os
import sys

sys.path += [os.curdir]

from .shell import shell

from .superuser import create_superuser
from .example import time
