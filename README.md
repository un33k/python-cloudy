Python Cloudy
====================

**A Python utility that simplifies cloud configuration**


Overview
========

A Python utility that simplifies server cloud configuration.


How to install
==================

    1. virtualenv cloudy
    2. source cloudy/bin/activate
    3. cd cloudy
    4. git clone http://github.com/un33k/python-cloudy
    5. pip install -e python-cloudy
    6. cd python-cloudy/cloudy
    7. fab -l
    8. optional [create a ~/.cloudy file based on the example in the cfg dir]


How to use
=================

``Usage``

    fab -l # list all the commands
    fab -H 10.10.10.10 -i ~/.ssh/key.pem sys_uname
    ..etc.


Running the tests
=================

To run the tests against the current environment:

    python test.py


License
====================

Released under a ([MIT](LICENSE)) license.


Version
====================
X.Y.Z Version

    `MAJOR` version -- when you make incompatible API changes,
    `MINOR` version -- when you add functionality in a backwards-compatible manner, and
    `PATCH` version -- when you make backwards-compatible bug fixes.


Sponsors
====================

[![Surge](https://www.surgeforward.com/wp-content/themes/understrap-master/images/logo.png)](https://github.com/surgeforward)
