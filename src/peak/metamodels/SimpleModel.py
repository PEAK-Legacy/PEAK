"""Add XMI reading and simple querying capabilities to the basic SEF model"""

from peak.api import *

import peak.metamodels.querying
import peak.model.api

__bases__ = (
    peak.metamodels.querying,
    peak.model.api,
)

config.setupModule()
