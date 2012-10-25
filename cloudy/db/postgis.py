import os
import re
import sys
from operator import itemgetter

from fabric.api import run
from fabric.api import task
from fabric.api import sudo
from fabric.api import put
from fabric.api import env
from fabric.api import settings
from fabric.api import hide

from cloudy.sys.etc import etc_git_commit









