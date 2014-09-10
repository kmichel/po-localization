# coding=utf-8

from distutils.core import setup

setup(
    name='po_localization',
    packages=['po_localization'],
    version='0.1.1',
    description='Localize Django applications without compiling .po files',
    author='Kevin Michel',
    author_email='kmichel.info@gmail.com',
    url='https://github.com/kmichel/po-localization',
    download_url='https://github.com/kmichel/po-localization/archive/v0.1.1.tar.gz',
    keywords=['django', 'localization'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Localization',
    ],
    requires=['django'],
)
