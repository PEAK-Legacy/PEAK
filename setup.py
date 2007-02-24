#!/usr/bin/env python
"""Distutils setup file"""

import sys, os, ez_setup
ez_setup.use_setuptools()

from setuptools import setup, Extension, Feature, find_packages

# Metadata
PACKAGE_NAME = "PEAK"
PACKAGE_VERSION = "0.5a4"
HAPPYDOC_IGNORE = [
    '-i','old', '-i','tests', '-i','setup', '-i','examples',
]


packages = find_packages('src')

extensions = [
    Extension("peak.util.pyexpat", [
        "src/peak/util/pyexpat.c",
        "src/expat/xmlparse.c", "src/expat/xmltok.c", #"src/expat/xmltok_ns.c",
        "src/expat/xmlrole.c",], #"src/expat/xmltok_impl.c"],
        include_dirs=["src/expat"],
        define_macros=[('XML_STATIC',1),('HAVE_MEMMOVE',1)]   # XXX
    ),
    Extension(
        "peak.binding._once", [
            "src/peak/binding/_once.pyx", "src/peak/binding/getdict.c"
        ]
    ),
    Extension("peak.util.buffer_gap", ["src/peak/util/buffer_gap.pyx"]),
    Extension("peak.util._Code", ["src/peak/util/_Code.pyx"]),
    Extension(
        "peak.persistence._persistence", ["src/peak/persistence/persistence.c"]
    ),
]




have_uuidgen = False

if os.name=='posix' and hasattr(os, 'uname'):

    un = os.uname()

    if un[0] == 'FreeBSD' and int(un[2].split('.')[0]) >= 5:
        have_uuidgen = True

    elif un[0] == 'NetBSD' and int(un[2].split('.')[0]) >= 2:
        have_uuidgen = True

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
                            have_uuidgen = True
        except:
            pass














execfile('src/setup/common.py')

features = {
    'tests': Feature(
        "test modules", standard = True,
        remove = [p for p in packages if p.endswith('.tests')]
    ),
    'metamodels': Feature(
        "MOF/UML metamodels", standard = True, remove=['peak.metamodels']
    ),
    'uuidgen': Feature(
        "UUID generation via BSD system libraries",
        available = have_uuidgen, standard = have_uuidgen,
        optional = have_uuidgen,
        ext_modules = [
            Extension("peak.util._uuidgen", ["src/peak/util/_uuidgen.c"]),
        ]
    ),
    'pyexpat-plus': Feature(
        "Backport pyexpat features from Python 2.4",
        standard=sys.version_info < (2,4), optional = False,
        remove = ["peak.util.pyexpat"]
    ),
}

ALL_EXTS = [
    '*.ini', '*.html', '*.conf', '*.xml', '*.pwt', '*.dtd', '*.txt',
]













setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,

    description="The Python Enterprise Application Kit",
    author="Phillip J. Eby",
    author_email="peak@eby-sarna.com",
    url="http://peak.telecommunity.com/",
    download_url="http://peak.telecommunity.com/snapshots/",
    license="PSF or ZPL",
    platforms=['UNIX','Windows'],
    package_dir = {'':'src'},
    packages    = packages,
    cmdclass = SETUP_COMMANDS,

    install_requires = [
        'RuleDispatch >= 0.5a0dev-r2287', 'PyProtocols  >= 1.0a0dev-r2287',
        'Importing    >= 1.9',            'SymbolType   >= 1.0',
        'wsgiref      >= 0.0.1dev',       'ZConfig      >  2.0',
        'DecoratorTools>=1.3',
    ],

    extras_require = {
        'FastCGI': ['fcgiapp >= 1.4'],
    },

    package_data = {
        '': ALL_EXTS,
        'peak.metamodels': ['*.asdl']
    },

    features = features,
    test_suite = 'peak.tests.test_suite',
    ext_modules = extensions,

    entry_points = {
        "console_scripts":["peak = peak.running.commands:__main__"]
    },
    zip_safe=sys.version>='2.3.5',


    long_description = """\
PEAK is an application kit, and applications are made from components.
PEAK provides you with a component architecture, component infrastructure,
and various general-purpose components and component frameworks for
building applications.  As with J2EE, the idea is to let you stop
reinventing architectural and infrastructure wheels, so you can put more
time into your actual application.

Development version: svn://svn.eby-sarna.com/svnroot/PEAK#egg=PEAK-dev
""",

    keywords = "Enterprise,SQL,LDAP,UML,XMI,JNDI,persistence,AOP,FastCGI,MOF,event-driven,twisted,web",

    classifiers = """
    Development Status :: 3 - Alpha
    Development Status :: 4 - Beta
    Environment :: Console
    Environment :: No Input/Output (Daemon)
    Environment :: Web Environment
    Environment :: Win32 (MS Windows)
    Intended Audience :: Developers
    License :: OSI Approved :: BSD License
    License :: OSI Approved :: Python Software Foundation License
    License :: OSI Approved :: Zope Public License
    Natural Language :: English
    Operating System :: Microsoft :: Windows
    Operating System :: POSIX
    Programming Language :: C
    Programming Language :: Python
    Topic :: Database :: Front-Ends
    Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries
    Topic :: Office/Business
    Topic :: Software Development :: Code Generators
    Topic :: Software Development :: Libraries :: Application Frameworks
    Topic :: Software Development :: Libraries :: Python Modules
    Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP
    Topic :: Text Processing :: Markup :: XML""".strip().splitlines()
)



