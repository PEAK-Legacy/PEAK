from peak.api import *
from interfaces import *
from places import Location

def finishComponent(parser,data):
    if 'sm.component' in data:
        return data['sm.component']

def findComponentData(data):
    prev = data['previous']   
    while 'sm.component' not in prev:
        prev = prev.get('previous')
    return prev
    
def startLocation(parser,data):
    attrs = dict(data['attributes'])
    prev = findComponentData(data)
    parent = prev['sm.component']
    data['sm.component'] = loc = Location(parent,attrs.get('name'))
    data['sm.sublocations'] = subloc = {}
    loc.addContainer(subloc)

def defineLocation(parser,data):
    data['finish'] = finishComponent
    data['start'] = startLocation
    prev = findComponentData(data)

    def addLocation(loc):
        data['sm.sublocations'][loc.getComponentName()] = loc
    data['child'] = addLocation

def setupDocument(parser,data):

    def setRoot(ob):
        data['sm.component'] = ob
    data['child'] = setRoot
    data['finish'] = finishComponent
    data['sm.component'] = data['parent']
    
