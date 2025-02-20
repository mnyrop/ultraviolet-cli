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
    'babel>=2.16.0',
    'click>=8.1.3',
    'Flask>=2.2.2',
    'Flask-Babel>=4.0.0',
    'invenio-app>=1.5.0',
    'invenio-base==1.4.0',
    'invenio-i18n>=2.1.2',
    'invenio-files-rest>=2.2.1',
    'invenio-access>=2.0.0',
    'invenio-accounts>=5.1.2',
    'invenio-pidstore>=1.3.1',
    'invenio-rdm-records>=10.8.6',
    'invenio-search>=2.4.1',
    'opensearch-dsl>=2.1.0',
    'opensearch-py>=2.7.1',
    'jsonschema>=4.23.0',
    'Sphinx>=7.3.7',
    'Werkzeug==2.2.2',
    'python-dotenv',
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