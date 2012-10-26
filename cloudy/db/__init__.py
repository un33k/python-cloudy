import os
import re
import types

PACKAGE = 'cloudy.db'
MODULE_RE = r"^.*.py$"
PREFIX = ['psql_', 'pgis_']

# Search through every file inside this module.
module_names = []
module_dir = os.path.dirname( __file__)
for filename in os.listdir(module_dir):
    if not re.match(MODULE_RE, filename) or filename == "__init__.py":
        continue
    # Import the module file and find all function inside it.
    module_module = __import__('%s.%s' % (PACKAGE, filename[:-3]),
                              {}, {},
                              filename[:-3])
    for name in dir(module_module):
        try:
            prefix = name.split('_')[0]+'_'
        except:
            continue

        if prefix in PREFIX:
            item = getattr(module_module, name)
            if not isinstance(item, (type, types.FunctionType)):
                continue

            # Found one, bring into the module namespace.
            exec "%s = item" % name
            module_names.append(name)

# Hide everything other than the classes from other modules.
__all__ = module_names
