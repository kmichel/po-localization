===========
Description
===========
* Localize Django applications without installing gettext, pybabel or compiling .po files.
* Automatically reload translations when any .po file is modified.
* Extract messages from templates and python files automatically or using a management command.

.. image:: https://travis-ci.org/kmichel/po-localization.svg
    :target: https://travis-ci.org/kmichel/po-localization
    :alt: Build Status

.. image:: https://pypip.in/py_versions/po_localization/badge.svg
    :target: https://pypi.python.org/pypi/po_localization/
    :alt: Supported Python Versions

.. image:: https://pypip.in/version/po_localization/badge.svg
    :target: https://pypi.python.org/pypi/po_localization/
    :alt: Latest Release

.. image:: https://pypip.in/license/po_localization/badge.svg
    :target: https://pypi.python.org/pypi/po_localization/
    :alt: License

============
Requirements
============
* python 2.7 or >= 3.2
* django >= 1.6

============
Installation
============
.. code-block:: bash

    $ pip install po-localization

=====
Setup
=====
Add ``'po_localization'`` to your ``INSTALLED_APPS``.

========
Settings
========
``AUTO_RELOAD_TRANSLATIONS = settings.DEBUG``
    | Whether translation files should be checked for modifications and reloaded before each request.
``AUTO_UPDATE_TRANSLATIONS = False``
    | Whether translation files should be automatically created or updated when templates or python files changes.
``UPDATE_TRANSLATIONS_PACKAGES = ()``
    | List of packages to update using the management command or when auto-update is enabled.
    | A 'locale' folder containing all translation files will be created or updated in each of those packages.
    | This 'locale' folder should be added to ``LOCALE_PATHS`` if the package is not a Django app.
``UPDATE_TRANSLATIONS_EXCLUDED_LOCALES = ()``
    | List of locales to exclude from update.
    | All locales from languages in ``LANGUAGES`` which are not in this exclusion list will be updated.
``UPDATE_TRANSLATIONS_WITH_LOCATIONS = True``
    | Whether translation files should include the locations of the extracted messages.
``UPDATE_TRANSLATIONS_PRUNE_OBSOLETES = False``
    | Whether obsolete translations should be pruned from translation files.
    | Empty translations will always be pruned.
    | Even if not pruned, obsolete translations will be marked as such with a comment.

===================
Management Commands
===================
``update_translations``
    Extract messages from templates and python files and create or update translation files.

======
Issues
======
If you have any suggestions, bug reports or annoyances please report them
to the issue tracker at https://github.com/kmichel/po-localization/issues .
