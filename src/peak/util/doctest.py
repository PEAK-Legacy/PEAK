import sys
if sys.version>='2.5':
   globals().update(__import__('doctest',{},{},[]).__dict__)
else:
   import _doctest
   globals().update(_doctest.__dict__)
