# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 NYU Libraries.
#
# ultraviolet-cli is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for custom Ultravaiolet commands"""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

tests_require = [
    'pytest-invenio>=1.4.0',
    'psycopg2>=2.9.5',
]

extras_require = {
    'docs': [
        'Sphinx>=3,<4',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for reqs in extras_require.values():
    extras_require['all'].extend(reqs)

setup_requires = [
    'Babel>=2.8',
]

install_requires = [
    'babel==2.10.3',
    'click>=8.1.3',
    'Flask>=2.2.2',
    'Flask-BabelEx>=0.9.4',
    'invenio-app>=1.3.4',
    'invenio-i18n>=1.2.0',
    'invenio-files-rest>=1.4.0',
    'invenio-access>=1.4.4',
    'invenio-accounts>=2.0.0',
    'invenio-pidstore>=1.2.3',
    'invenio-rdm-records>=1.3.6',
    'invenio-search>=2.1.0',
    'jsonschema>=4.17.3',
    'opensearch-dsl>=2.0.0',
    'opensearch-py>=2.0.0',
    'redis>=5.0.0b4',
    'Sphinx>=3,<4',
    'Werkzeug==2.2.2',
    'invenio-app-rdm',
    'check-manifest',
    'pytest',
    'invenio-cli'
]


packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('ultraviolet_cli', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='ultraviolet-cli',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='invenio TODO',
    license='MIT',
    author='NYU Libraries',
    author_email='nyu-data-repository@nyu.edu',
    url='https://github.com/nyudlts/ultraviolet-cli',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'console_scripts': [
            'ultraviolet-cli=ultraviolet_cli.cli:cli',
            'uv-cli=ultraviolet_cli.cli:cli' # alias shorthand
        ]
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3.9',
        'Development Status :: 1 - Planning',
    ],
)
