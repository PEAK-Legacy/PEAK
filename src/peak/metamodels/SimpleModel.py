"""Add XMI reading and simple querying capabilities to the basic SEF model"""

from peak.api import *

import peak.metamodels.xmi.Reading
import peak.metamodels.querying
import peak.metamodels.FeatureObjects

__bases__ = (
    peak.metamodels.xmi.Reading,
    peak.metamodels.querying,
    peak.metamodels.FeatureObjects,
)

binding.setupModule()
