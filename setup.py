#!/usr/bin/env python
"""Distutils setup file"""

from distutils.core import setup, Command
from distutils.command.install_data import install_data
from distutils.command.sdist import sdist as old_sdist

class install_data(install_data):

    """Variant of 'install_data' that installs data to module directories"""
    
    def finalize_options (self):
        self.set_undefined_options('install',
                                   ('install_purelib', 'install_dir'),
                                   ('root', 'root'),
                                   ('force', 'force'),
                                  )

class sdist(old_sdist):

    """Variant of 'sdist' that (re)builds the documentation first"""
   
    def run(self):

        # Build docs before source distribution
        self.run_command('happy')

        # Run the standard sdist command
        old_sdist.run(self)












class happy(Command):

    """Command to generate documentation using HappyDoc

        I should probably make this more general, and contribute it to either
        HappyDoc or the distutils, but this does the trick for TW for now...
    """

    description = "Generate docs using happydoc"

    user_options = []


    def initialize_options(self):
        self.happy_options = None
        self.doc_output_path = None


    def finalize_options(self):

        if self.doc_output_path is None:
            self.doc_output_path = 'docs/html/reference'

        if self.happy_options is None:
            self.happy_options = [
                '-t', 'TransWarp Reference', '-d', self.doc_output_path,
                '-i', 'examples', '-i', 'old', '-i', 'tests', '.',
            ]
            if not self.verbose: self.happy_options.insert(0,'-q')

    def run(self):
        from distutils.dir_util import remove_tree, mkpath
        from happydoclib import HappyDoc

        mkpath(self.doc_output_path, 0755, self.verbose, self.dry_run)
        remove_tree(self.doc_output_path, self.verbose, self.dry_run)

        if not self.dry_run:
            HappyDoc(self.happy_options).run()


setup(

    name="TransWarp",
    version="0.2pre1",
    description="The TransWarp Software Automation Toolkit",
    
    author="Phillip J. Eby",
    author_email="transwarp@eby-sarna.com",
    
    url="http://www.telecommunity.com/TransWarp/",
    
    packages=[
        'TW', 'TW.API', 'TW.Database', 'TW.MOF', 'TW.SEF', 'TW.UML', 'TW.XMI',
        'TW.Utils', 'TW.API.tests', 'TW.Database.tests', 'TW.SEF.tests',
        'TW.Utils.tests', 'TW.tests', 
    ],
    
    package_dir = {'':'src'},

    cmdclass = {'install_data': install_data, 'sdist': sdist, 'happy': happy},
    
    data_files = [
        ('TW/SEF/tests', ['src/TW/SEF/tests/MetaMeta.xml']),
    ],
)


