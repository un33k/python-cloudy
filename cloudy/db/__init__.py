import os
import re
import types

PACKAGE = 'cloudy.db'
MODULE_RE = r"^.*.py$"
PREFIX = ['db_']
SKIP = ['.', '..', '__init__.py']

# Examine every file inside this module
functions = []
module_dir = os.path.dirname( __file__)
for fname in os.listdir(module_dir):
    if fname not in SKIP and re.match(MODULE_RE, fname):
        module = __import__('{0}.{1}'.format(PACKAGE, fname[:-3]), {}, {}, fname[:-3])
        for name in dir(module):
            try:
                prefix = name.split('_')[0]+'_'
            except:
                continue
            if prefix in PREFIX:
                item = getattr(module, name)
                if not isinstance(item, (type, types.FunctionType)):
                    continue

                # matched! bring into the module namespace.
                exec '{0} = item'.format(name)
                functions.append(name)

# Only reveal the functions with match prefix and hide everything else from this module.
__all__ = functions
