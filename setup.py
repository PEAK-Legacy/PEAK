#!/usr/bin/env python

"""Distutils setup file"""

from distutils.core import Extension
from os.path import join, walk
from os import sep
import fnmatch

include_tests = True        # edit this to stop installation of test modules
include_metamodels = True   # edit this to stop installation of MOF, UML, etc.


try:
    import Pyrex.Distutils
    EXT = '.pyx'

except ImportError:
    EXT = '.c'


def findDataFiles(dir, skipDepth, *globs):

    def visit(out, dirname, names):
	n = []
        for pat in globs:
            n.extend(fnmatch.filter(names,pat))
        if n:
            instdir = sep.join(dirname.split(sep)[skipDepth:])
            out.append( (instdir, [join(dirname,f) for f in n]) )

    out = []
    walk(dir,visit,out)
    return out



# Metadata

PACKAGE_NAME = "PEAK"
PACKAGE_VERSION = "0.5a0"

HAPPYDOC_IGNORE = [
    '-i', 'examples',  '-i', 'old', '-i', 'tests',
]


# Base packages for installation

packages = [
    'peak', 'peak.api', 'peak.binding', 'peak.config', 'peak.model',
    'peak.naming', 'peak.naming.factories', 'peak.running',
    'peak.storage', 'peak.util',
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
        'zope', 'zope.interface', 'zope.interface.common',
        'persistence', 'ZConfig',
    ]

    extensions += [
        Extension("persistence._persistence", ["src/persistence/persistence.c"])
    ]

    if include_tests:
        packages += [
            'zope.interface.tests', 'persistence.tests', 'ZConfig.tests',
            'zope.interface.common.tests',
        ]

        data_files += findDataFiles('src/ZConfig/tests', 1, '*.xml', '*.txt', '*.conf')



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

    ext_modules = extensions,
)


