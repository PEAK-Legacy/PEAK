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
    '-i','datetime', '-i','old', '-i','tests', '-i','setup', '-i','examples',
    '-i', 'kjbuckets', '-i', 'ZConfig', '-i', 'persistence', '-i', 'csv',
]

# Base packages for installation
scripts = ['scripts/peak']
packages = [
    'peak', 'peak.api', 'peak.binding', 'peak.config', 'peak.model',
    'peak.naming', 'peak.naming.factories', 'peak.net', 'peak.running',
    'peak.tools', 'peak.tools.n2', 'peak.security', 'peak.tools.supervisor',
    'peak.storage', 'peak.util', 'peak.web', 'peak.ddt', 'protocols',
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


if include_tests:

    packages += [
        'peak.tests', 'peak.binding.tests', 'peak.config.tests',
        'peak.model.tests', 'peak.naming.tests', 'peak.running.tests',
        'peak.security.tests', 'peak.web.tests', 'peak.query.tests',
        'peak.storage.tests', 'peak.util.tests', 'protocols.tests',
        'peak.events.tests', 'peak.ddt.tests',
    ]


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
            'persistence.tests', 'ZConfig.tests', 'ZConfig.tests.library',
            'ZConfig.tests.library.thing', 'ZConfig.tests.library.widget',
        ]















import sys

if sys.version_info < (2,3):
    # Install datetime and csv if we're not on 2.3

    packages += ['datetime','csv']
    if include_tests:
        packages += ['datetime.tests']

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

    uuidgen = False
    if hasattr(os, 'uname'):
        un = os.uname()
        if un[0] == 'FreeBSD' and int(un[2].split('.')[0]) >= 5:
            uuidgen = True
        elif un[0] == 'NetBSD' and int(un[2].split('.')[0]) >= 2:
            uuidgen = True
        elif un[0] == 'NetBSD' and un[2].startswith('1.6Z'):
            # XXX for development versions before 2.x where uuidgen
            # is present -- this should be removed at some point
            try:
                if len(un[2]) > 4:
                    if ord(un[2][4]) >= ord('I'):
                        if os.path.exists('/lib/libc.so.12'):
                            l = os.listdir('/lib')
                            l = [x for x in l if x.startswith('libc.so.12.')]
                            l = [int(x.split('.')[-1]) for x in l]
                            l.sort(); l.reverse()
                            if l[0] >= 111:
                                uuidgen = True
            except:
                pass

    if uuidgen:
        extensions += [
            Extension("peak.util._uuidgen", ["src/peak/util/_uuidgen" + EXT]),
        ]




execfile('src/setup/common.py')
from setuptools import setup

ALL_EXTS = [
    '*.ini', '*.html', '*.conf', '*.xml', '*.pwt', '*.dtd', '*.txt',
]
    
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

    package_data = {
        '': ALL_EXTS,
        'ZConfig.tests': ['input/*.xml', 'input/*.conf'],
        'ZConfig.tests.library.thing': ['extras/extras.xml'],
        'peak.metamodels': ['*.asdl']
    },

    test_module = TEST_MODULE,
    ext_modules = extensions,
    scripts = scripts,
)








