"""Exceptions for peak.naming package"""

__all__ = [
    'NamingException', 'InvalidNameException', 'NameNotFoundException',
    'CannotProceedException', 'NotContextException',
]



































class NamingException(Exception):

    """Base class for all peak.naming exceptions

        Supports the following constructor keyword arguments, which then
        become attributes of the exception object:

            rootException -- Exception that caused this exception to be thrown.
        
            rootTraceback -- Traceback of the root exception.
        
            resolvedName -- The portion of the name that was successfully
                resolved.

            resolvedObj -- The object through which resolution was successful,
                i.e., the object to which 'resolvedName' is bound.
            
            remainingName -- The remaining portion of the name which could not
                be resolved.

        The constructor also accepts an arbitrary number of unnamed arguments,
        which are treated the way arguments to the standard Exception class
        are treated.  (That is, saved in the 'args' attribute and used in the
        '__str__' method for formatting.)
    """

    formattables = ('resolvedName', 'remainingName', 'rootException',)
    otherattrs   = ('resolvedObj', 'rootTraceback', 'args', )

    __slots__ = list( formattables + otherattrs )


    def __init__(self, *args, **kw):

        for k in self.extras:
            setattr(self,k,kw.get(k))

        self.args = args



    def __str__(self):

        """Format the exception"""

        txt = super(NamingException,self).__str__(self)
        
        extras = [
            '%s=%s' % (k,getattr(self,k))
            for k in self.formattables if getattr(self,k) is not None
        ]

        if extras:
            return "%s [%s]" % (txt, ','.join(extras))
            
        return txt


class InvalidNameException(NamingException):
    """Unparseable string or non-name object"""
   

class NameNotFoundException(NamingException, LookupError):
    """A name could not be found"""

class NotContextException(NamingException):
    """Continuation is not a context/does not support required interface"""
















