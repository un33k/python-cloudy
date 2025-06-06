from cloudy.db import *
from cloudy.sys import *
from cloudy.aws import *
from cloudy.srv import *
from cloudy.web import *
from fabric.api import env
import logging

# Set global logging level to ERROR for cleaner output
logging.basicConfig(level=logging.ERROR)
