#!/usr/bin/env python

from distutils.core import setup

setup(
    name="TransWarp",
    version="0.2pre1",
    description="The TransWarp Software Automation Toolkit",
    author="Phillip J. Eby",
    author_email="transwarp@eby-sarna.com",
    url="http://www.zope.org/Members/pje/Wikis/TransWarp",
    packages=[
        'TW', 'TW.API', 'TW.Database', 'TW.MOF', 'TW.StructuralModel', 'TW.UML',
        'TW.Utils', 'TW.XMI', 'TW.tests', 'TW.tests.Database',
        'TW.tests.StructuralModel',
    ],
    package_dir = {'':'src'},
    data_files = [
        ('TW/tests/StructuralModel', ['src/TW/tests/StructuralModel/MetaMeta.xml']),
    ],
)


