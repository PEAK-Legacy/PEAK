TransWarp Preview Release 0.1

 Copyright (C) 2001 Phillip J. Eby, All rights reserved.
 This software may be used under the same terms as Zope or Python.

 Please see "The TransWarp Wiki":http://www.zope.org/Members/pje/Wikis/TransWarp
 for tutorials, FAQs, package layout, etc.  Selected pages from the Wiki are
 included in the 'docs/' directory for your convenience.

 At this time, the 'Features', 'Aspects', 'SOX', and 'tests' modules
 and packages are usable, if not necessarily full-featured.  All other
 modules/packages (except as imported by the above) are under heavy
 construction - don't enter without a hard hat!  (That is,
 use them at your own risk.  Although, there's no warranty that any of
 the other stuff works, beyond the fact that the tests run on my
 home computer.)


 INSTALLATION INSTRUCTIONS

  To use this package, you will need to install it by placing the TW/ directory
  inside a directory which is listed in your Python path.  You will also need
  to install Aaron Watters' "kjbuckets" library, and Jim Fulton's "Scarecrow"
  Interfaces package.

  Later versions will hopefully automate some of this as we learn to use the
  Python distutils, but for now, you have to do everything yourself...

  Getting and Installing kjbuckets

   Unix Platforms

    You can download the C source code for kjbuckets at:

     "http://www.chordate.com/kjbuckets/":http://www.chordate.com/kjbuckets/

    And build as you would any other Python module.

   Windows Platforms

    If you're using Python 1.5, you can download a pre-built kjbuckets.pyd at:

     "http://www.chordate.com/kwParsing/kjbuckets.pyd":http://www.chordate.com/kwParsing/kjbuckets.pyd

    And then place it in your Python path.  If you're using Python 2.0,
    or can't get this to work, see "If You Can't Compile kjbuckets" below.

   If You Can't Compile kjbuckets

    If for whatever reason you can't get the C version of kjbuckets to work
    on your system, download this file:

     "http://www.chordate.com/kwParsing/kjbuckets0.py":http://www.chordate.com/kwParsing/kjbuckets0.py

    Rename it to "kjbuckets.py", and place it in your Python path.  This runs
    slower than the C version, but it'll do in a pinch.

  Getting and Installing the Interface package (aka "The Scarecrow")

   The easiest place to find a copy of the Interface package is in the
   lib/python directory of a Zope installation.  Just copy it over to your
   main Python path, or add the lib/python directory to your Python path.

   Failing that, you can look at this URL for downloads:

    "http://www.zope.org/Members/michel/Products/Interfaces/":http://www.zope.org/Members/michel/Products/Interfaces/

   This may not be the best place for an up-to-date copy, but the current
   TransWarp code doesn't do much with interfaces yet, so it probably doesn't
   matter right now.


 TESTING YOUR INSTALLATION

  TransWarp comes with a fairly hefty built-in test suite.  If you have
  the Python "unittest" module installed in your Python path, you can use
  it to run the test suites, like this::

   python unittest.py TW.tests.suite

  This will run about 114 tests on various parts of TransWarp.  If you have
  installed everything correctly, 100% of the tests should succeed.  If
  you're missing any needed parts, you will probably experience a massive
  number of failures and errors.

