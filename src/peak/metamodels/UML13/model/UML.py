# ------------------------------------------------------------------------------
# Package: peak.metamodels.UML13.model.UML
# File:    peak\metamodels\UML13\model\UML.py
# ------------------------------------------------------------------------------

from peak.util.imports import lazyModule as _lazy

_model               = _lazy('peak.model.api')
_config              = _lazy('peak.config.api')
_datatypes           = _lazy('peak.model.datatypes')

Foundation           = _lazy(__name__, '../Foundation')
Behavioral_Elements  = _lazy(__name__, '../Behavioral_Elements')
Model_Management     = _lazy(__name__, '../Model_Management')

# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------

_config.setupModule()


