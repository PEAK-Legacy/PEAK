"""Add XMI reading and simple querying capabilities to the basic SEF model"""

from TW.API import *

import TW.XMI.Reading
import TW.SEF.Queries
import TW.SEF.Basic 

__bases__ = TW.XMI.Reading, TW.SEF.Queries, TW.SEF.FeatureObjects

setupModule()
