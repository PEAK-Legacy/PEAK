#!/usr/bin/env python
"""Distutils setup file"""

from distutils.core import setup
from distutils.command.install_data import install_data

class install_data(install_data):

    def finalize_options (self):
        self.set_undefined_options('install',
                                   ('install_purelib', 'install_dir'),
                                   ('root', 'root'),
                                   ('force', 'force'),
                                  )

setup(

    name="TransWarp",
    version="0.2pre1",
    description="The TransWarp Software Automation Toolkit",
    
    author="Phillip J. Eby",
    author_email="transwarp@eby-sarna.com",
    
    url="http://www.zope.org/Members/pje/Wikis/TransWarp",
    
    packages=[
        'TW', 'TW.API', 'TW.Database', 'TW.MOF', 'TW.SEF', 'TW.UML', 'TW.XMI',
        'TW.Utils', 'TW.API.tests', 'TW.Database.tests', 'TW.SEF.tests',
        'TW.Utils.tests', 'TW.tests', 
    ],
    
    package_dir = {'':'src'},

    cmdclass = {'install_data': install_data},
    
    data_files = [
        ('TW/SEF/tests', ['src/TW/SEF/tests/MetaMeta.xml']),
    ],
)


