"""Domain logic and convenience features for manipulating UML Models"""

from peak.api import config
from peak.util.imports import lazyModule


# Inherit from the generated code (for the __init__ module)
__bases__ = lazyModule(__name__, '../model/Foundation'),


# Inherit modules from generated code
__path__.extend(__bases__[0].__path__)


config.setupModule()

