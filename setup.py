#!/usr/bin/env python
"""Distutils setup file"""

execfile('src/setup/prologue.py')

include_tests      = True   # edit this to stop installation of test modules
include_metamodels = True   # edit this to stop installation of MOF, UML, etc.
include_fcgiapp    = True   # edit this to stop installation of 'fcgiapp'

# Metadata
PACKAGE_NAME = "PEAK"
PACKAGE_VERSION = "0.5a3"
HAPPYDOC_IGNORE = [
    '-i', 'examples',  '-i', 'old', '-i', 'tests', '-i', 'setup',
    '-i', 'kjbuckets', '-i', 'ZConfig', '-i', 'persistence',
]

# Base packages for installation
scripts = ['scripts/peak']
modules = []
packages = [
    'peak', 'peak.api', 'peak.binding', 'peak.config', 'peak.model',
    'peak.naming', 'peak.naming.factories', 'peak.net', 'peak.running',
    'peak.tools', 'peak.tools.n2', 'peak.security', 'peak.tools.supervisor',
    'peak.storage', 'peak.util', 'peak.web', 'protocols',
    'peak.tools.version', 'peak.query', 'peak.events',
]

extensions = [
    Extension("kjbuckets", ["src/kjbuckets/kjbucketsmodule.c"]),
    Extension(
        "peak.binding._once", [
            "src/peak/binding/_once" + EXT,
            "src/peak/binding/getdict.c"
        ]
    ),
    Extension("peak.util.buffer_gap", ["src/peak/util/buffer_gap" + EXT]),
    Extension("peak.util._Code", ["src/peak/util/_Code" + EXT]),
    Extension("protocols._speedups", ["src/protocols/_speedups" + EXT]),
]

# Base data files

data_files = [
    ('peak',     ['src/peak/peak.ini']),
    ('peak/web', ['src/peak/web/resource_defaults.ini']),
    ('ZConfig/doc', ['src/ZConfig/doc/schema.dtd']),
] + findDataFiles('src/peak/running', 1, '*.xml', '*.ini')


if include_tests:
    packages += [
        'peak.tests', 'peak.binding.tests', 'peak.config.tests',
        'peak.model.tests', 'peak.naming.tests', 'peak.running.tests',
        'peak.security.tests', 'peak.web.tests', 'peak.query.tests',
        'peak.storage.tests', 'peak.util.tests', 'protocols.tests',
        'peak.events.tests'
    ]
    data_files += [
        ('peak/running/tests', ['src/peak/running/tests/test_cluster.txt']),
        ('peak/config/tests',  ['src/peak/config/tests/test_links.ini']),
    ] + findDataFiles('src/peak/web/tests', 1, '*.pwt')


if include_metamodels:

    packages += [
        'peak.metamodels',
        'peak.metamodels.UML13', 'peak.metamodels.UML14',
        'peak.metamodels.UML13.model', 'peak.metamodels.UML14.model',
        'peak.metamodels.UML13.model.Foundation',
        'peak.metamodels.UML13.model.Behavioral_Elements',
    ]

    if include_tests:

        packages += [ 'peak.metamodels.tests' ]

        data_files += findDataFiles(
            'src/peak/metamodels/tests', 1, '*.xml', '*.asdl'
        )

try:
    # Check if Zope X3 is installed; we use zope.component
    # because we don't install it ourselves; if we used something we
    # install, we'd get a false positive if PEAK was previously installed.
    import zope.component
    zope_installed = True

except ImportError:
    zope_installed = False


if not zope_installed:

    packages += [
        'persistence', 'ZConfig',
    ]

    extensions += [
        Extension("persistence._persistence", ["src/persistence/persistence.c"])
    ]

    if include_tests:
        packages += [
            'persistence.tests', 'ZConfig.tests',
        ]

        data_files += findDataFiles(
            'src/ZConfig/tests', 1, '*.xml', '*.txt', '*.conf'
        )












import sys

if sys.version_info < (2,3):
    # Install datetime and csv if we're not on 2.3

    packages += ['datetime']
    if include_tests:
        packages += ['datetime.tests']

    modules += ['csv']
    extensions += [
        Extension('_csv', ['src/_csv.c'])
    ]

import os

if os.name=='posix':

    # install 'fcgiapp' module on posix systems
    if include_fcgiapp:
        extensions += [
            Extension("fcgiapp", [
                "src/fcgiapp/fcgiappmodule.c", "src/fcgiapp/fcgiapp.c"
            ])
        ]
















execfile('src/setup/common.py')

setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,

    description="The Python Enterprise Application Kit",
    author="Phillip J. Eby",
    author_email="transwarp@eby-sarna.com",
    url="http://peak.telecommunity.com/",
    license="PSF or ZPL",
    platforms=['UNIX','Windows'],

    package_dir = {'':'src'},
    packages    = packages,
    cmdclass = SETUP_COMMANDS,
    data_files = data_files,
    ext_modules = extensions,
    scripts = scripts,
)





















