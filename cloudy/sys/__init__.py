import os
import re
import types
import importlib

PACKAGE = 'cloudy.sys'
MODULE_RE = r"^[^.].*\.py$"
PREFIX = ['sys_']
SKIP = {'__init__.py'}

functions = []
module_dir = os.path.dirname(__file__)

for fname in os.listdir(module_dir):
    if fname in SKIP or not re.match(MODULE_RE, fname):
        continue
    mod_name = fname[:-3]
    module = importlib.import_module(f'{PACKAGE}.{mod_name}')
    for name in dir(module):
        if any(name.startswith(p) for p in PREFIX):
            item = getattr(module, name)
            if isinstance(item, types.FunctionType):
                globals()[name] = item
                functions.append(name)

__all__ = functions
