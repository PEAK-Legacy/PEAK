##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Interfaces for standard python exceptions

$Id: interfaces.py,v 1.1 2003/02/11 16:00:07 pje Exp $
"""
from zope.interface import Interface
from zope.interface.implements import implements

class IException(Interface): pass
class IStandardError(IException): pass
class IWarning(IException): pass
class ISyntaxError(IStandardError): pass
class ILookupError(IStandardError): pass
class IValueError(IStandardError): pass
class IRuntimeError(IStandardError): pass
class IArithmeticError(IStandardError): pass
class IAssertionError(IStandardError): pass
class IAttributeError(IStandardError): pass
class IDeprecationWarning(IWarning): pass
class IEOFError(IStandardError): pass
class IEnvironmentError(IStandardError): pass
class IFloatingPointError(IArithmeticError): pass
class IIOError(IEnvironmentError): pass
class IImportError(IStandardError): pass
class IIndentationError(ISyntaxError): pass
class IIndexError(ILookupError): pass
class IKeyError(ILookupError): pass
class IKeyboardInterrupt(IStandardError): pass
class IMemoryError(IStandardError): pass
class INameError(IStandardError): pass
class INotImplementedError(IRuntimeError): pass
class IOSError(IEnvironmentError): pass
class IOverflowError(IArithmeticError): pass
class IOverflowWarning(IWarning): pass
class IReferenceError(IStandardError): pass
class IRuntimeWarning(IWarning): pass
class IStopIteration(IException): pass
class ISyntaxWarning(IWarning): pass
class ISystemError(IStandardError): pass
class ISystemExit(IException): pass
class ITabError(IIndentationError): pass
class ITypeError(IStandardError): pass
class IUnboundLocalError(INameError): pass
class IUnicodeError(IValueError): pass
class IUserWarning(IWarning): pass
class IZeroDivisionError(IArithmeticError): pass

implements(ArithmeticError, IArithmeticError)
implements(ArithmeticError, IArithmeticError)
implements(AssertionError, IAssertionError)
implements(AttributeError, IAttributeError)
implements(DeprecationWarning, IDeprecationWarning)
implements(EOFError, IEOFError)
implements(EnvironmentError, IEnvironmentError)
implements(Exception, IException)
implements(FloatingPointError, IFloatingPointError)
implements(IOError, IIOError)
implements(ImportError, IImportError)
implements(IndentationError, IIndentationError)
implements(IndexError, IIndexError)
implements(KeyError, IKeyError)
implements(KeyboardInterrupt, IKeyboardInterrupt)
implements(LookupError, ILookupError)
implements(MemoryError, IMemoryError)
implements(NameError, INameError)
implements(NotImplementedError, INotImplementedError)
implements(OSError, IOSError)
implements(OverflowError, IOverflowError)
implements(OverflowWarning, IOverflowWarning)
implements(ReferenceError, IReferenceError)
implements(RuntimeError, IRuntimeError)
implements(RuntimeWarning, IRuntimeWarning)
implements(StandardError, IStandardError)
implements(StopIteration, IStopIteration)
implements(SyntaxError, ISyntaxError)
implements(SyntaxWarning, ISyntaxWarning)
implements(SystemError, ISystemError)
implements(SystemExit, ISystemExit)
implements(TabError, ITabError)
implements(TypeError, ITypeError)
implements(UnboundLocalError, IUnboundLocalError)
implements(UnicodeError, IUnicodeError)
implements(UserWarning, IUserWarning)
implements(ValueError, IValueError)
implements(Warning, IWarning)
implements(ZeroDivisionError, IZeroDivisionError)

