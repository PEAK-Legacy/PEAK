"""Standard property names for the naming package"""

from names import PropertyName

__all__ = [
    'CREATION_PARENT', 'OBJECT_FACTORIES', 'STATE_FACTORIES', 'SCHEMES_PREFIX',
    'CREATION_NAME', 'INIT_CTX_FACTORY'
]

INIT_CTX_FACTORY = PropertyName('peak.naming.initialContextFactory')

CREATION_NAME    = PropertyName('peak.naming.creationName')
CREATION_PARENT  = PropertyName('peak.naming.creationParent')
OBJECT_FACTORIES = PropertyName('peak.naming.objectFactories')
STATE_FACTORIES  = PropertyName('peak.naming.stateFactories')

SCHEMES_PREFIX   = PropertyName('peak.naming.schemes')

