#!/usr/bin/env python

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
        'TW', 'TW.API', 'TW.Database', 'TW.MOF', 'TW.StructuralModel', 'TW.UML',
        'TW.Utils', 'TW.XMI', 'TW.tests', 'TW.tests.Database',
        'TW.tests.StructuralModel',
    ],
    
    package_dir = {'':'src'},

    cmdclass = {'install_data': install_data},
    
    data_files = [
        ('TW/tests/StructuralModel', ['src/TW/tests/StructuralModel/MetaMeta.xml']),
    ],
)


