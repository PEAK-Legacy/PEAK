#!/usr/bin/env python

"""Distutils setup file"""

from distutils.core import setup, Command
from distutils.command.install_data import install_data
from distutils.command.sdist import sdist as old_sdist
import sys

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










class test(Command):

    """Command to run unit tests after installation"""

    description = "Run unit tests after installation"

    user_options = [('test-module=','m','Test module (default=peak.tests)'),]

    def initialize_options(self):
        self.test_module = None

    def finalize_options(self):

        if self.test_module is None:
            self.test_module = 'peak.tests'

        self.test_args = [self.test_module+'.test_suite']

        if self.verbose:
            self.test_args.insert(0,'--verbose')

    def run(self):

        # Install before testing
        self.run_command('install')

        if not self.dry_run:
            from unittest import main
            main(None, None, sys.argv[:1]+self.test_args)












class happy(Command):

    """Command to generate documentation using HappyDoc

        I should probably make this more general, and contribute it to either
        HappyDoc or the distutils, but this does the trick for PEAK for now...
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
                '-t', 'PEAK Reference', '-d', self.doc_output_path,
                '-i', 'examples', '-i', 'old', '-i', 'tests',
                '-i', 'Interface', '.'
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

    name="PEAK",
    version="0.5a1",
    description="The Python Enterprise Application Kit",
    
    author="Phillip J. Eby",
    author_email="transwarp@eby-sarna.com",
    
    url="http://www.telecommunity.com/PEAK/",
    
    packages=[
        'peak', 'peak.api', 'peak.binding', 'peak.model', 'peak.metamodels',
        'peak.metamodels.mof', 'peak.metamodels.uml', 'peak.metamodels.xmi',
        'peak.naming', 'peak.naming.factories', 'peak.util', 'peak.running',
        'peak.config', 'peak.storage',

        'peak.binding.tests',
        'peak.metamodels.tests', 'peak.util.tests', 'peak.tests',

        'Interface', 'Interface.Common', 'Interface.tests',
    ],
    
    package_dir = {'':'src'},

    cmdclass = {
        'install_data': install_data, 'sdist': sdist, 'happy': happy,
        'test': test,
    },
    
    data_files = [
        ('peak/metamodels/tests', ['src/peak/metamodels/tests/MetaMeta.xml']),
    ],
)


