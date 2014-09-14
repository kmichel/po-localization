===========
Description
===========
| Localize Django applications without compiling .po files.
| Also optionally live-reload localizations if any .po file is modified.

============
Requirements
============
* python 2.7 or >= 3.2
* django >= 1.6

============
Installation
============
.. code-block:: bash

    $ git clone https://github.com/kmichel/po-localization
    $ python setup.py install

=====
Setup
=====
Add ``'po_localization'`` to your ``INSTALLED_APPS``.

========
Settings
========
``AUTORELOAD_TRANSLATIONS`` :
    | Whether translations should be checked for modifications and reloaded before each request.
    | By default it has the same value as your ``DEBUG`` setting.

======
Issues
======
If you have any suggestions, bug reports or annoyances please report them
to the issue tracker at https://github.com/kmichel/po-localization/issues .
