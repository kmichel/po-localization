# coding=utf-8

from setuptools import setup

__version__ = 'unknown'
with open('po_localization/version.py') as version_file:
    exec(version_file.read())

with open('README.rst') as readme_file:
    long_description = readme_file.read()

setup(
    name='po_localization',
    packages=[
        'po_localization',
        'po_localization.management',
        'po_localization.management.commands',
        'po_localization.tests',
        'po_localization.tests.test_app',
        'po_localization.tests.test_project'],
    package_data={
        'po_localization.tests': ['*.html', '*.po'],
        'po_localization.tests.test_app': ['templates/*.html'],
        'po_localization.tests.test_project': ['locale/fr/LC_MESSAGES/*.po'],
    },
    version=__version__,
    description='Localize Django applications without compiling .po files',
    long_description=long_description,
    author='Kevin Michel',
    author_email='kmichel.info@gmail.com',
    url='https://github.com/kmichel/po-localization',
    download_url='https://github.com/kmichel/po-localization/archive/v{}.tar.gz'.format(__version__),
    keywords=['django', 'localization'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Localization',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=['django>=1.6'],
)
