Cloudy
====================

**A Python utility that simplifies cloud configuration**

**Author:** Val Neekman [ info@neekware.com, @vneekman ]

Overview
========

A Python utility that simplifies cloud configuration.

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
    
``Note:``

Running the tests
=================

To run the tests against the current environment:

    python test.py

Changelog
=========

0.1
-----

* Initial release


License
=======

Copyright (c) 2012, Val Neekman

Neekware Inc.

All rights reserved.

Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this 
list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this 
list of conditions and the following disclaimer in the documentation and/or 
other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE 
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.



