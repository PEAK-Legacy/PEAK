#!/usr/bin/env python

"""Distutils setup file"""

include_tests = True        # edit this to stop installation of test modules
include_metamodels = True   # edit this to stop installation of MOF, UML, etc.

# Metadata

PACKAGE_NAME = "PEAK"
PACKAGE_VERSION = "0.5a0"

HAPPYDOC_IGNORE = [
    '-i', 'examples',  '-i', 'old', '-i', 'tests',
    '-i', 'Interface', '-i', 'Persistence', '-i', 'kjbuckets',
]


# Base packages for installation

packages = [
    'peak', 'peak.api', 'peak.binding', 'peak.config', 'peak.model',
    'peak.naming', 'peak.naming.factories', 'peak.running',
    'peak.storage', 'peak.util',

    'Interface', 'Interface.Common', 'Interface.Registry',
    'Persistence',
]


# Base data files

data_files = [
    ('peak', ['src/peak/peak.ini']),
]






if include_tests:

    packages += [
        'peak.tests', 'peak.binding.tests', 'peak.config.tests',
        'peak.model.tests', 'peak.naming.tests', 'peak.running.tests',
        'peak.storage.tests', 'peak.util.tests',

        'Interface.tests', 'Interface.Common.tests',
        'Interface.Registry.tests',
    ]

    data_files += [
        ('peak/running/tests', ['src/peak/running/tests/test_cluster.txt']),
    ]


if include_metamodels:

    packages += [
        'peak.metamodels',
        'peak.metamodels.UML13',
        'peak.metamodels.UML13.model',
        'peak.metamodels.UML13.model.Foundation',
        'peak.metamodels.UML13.model.Behavioral_Elements',
    ]

    if include_tests:

        packages += [
            'peak.metamodels.tests',
        ]

        data_files += [
            ('peak/metamodels/tests',
                ['src/peak/metamodels/tests/MetaMeta.xml']
            ),
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

    packages    = packages,
    package_dir = {'':'src'},

    cmdclass = SETUP_COMMANDS,

    data_files = data_files,

    ext_modules = [
        Extension("kjbuckets", ["src/kjbuckets/kjbucketsmodule.c"]),
        Extension("Persistence.cPersistence",
            ["src/Persistence/cPersistence.c"]
        ),
        Extension(
            "peak.binding._once", [
                "src/peak/binding/_once" + EXT,
                "src/peak/binding/getdict.c"
            ]
        ),
        Extension("peak.util.buffer_gap", ["src/peak/util/buffer_gap" + EXT]),
        Extension("peak.util._Code", ["src/peak/util/_Code" + EXT]),
    ],

)


