from peak.api import *
from unittest import TestCase, makeSuite, TestSuite
from cStringIO import StringIO






































class MailModel(model.Model, storage.xmi.Loader):

    class Letter(model.Element):

        class envelope(model.Reference):
            referencedType = 'Envelope'
            referencedEnd  = 'letter'

    class Envelope(model.Element):

        class toAddress(model.Field):   referencedType = 'Address'
        class fromAddress(model.Field): referencedType = 'Address'

        class letters(model.Collection):
            _XMINames = 'letter',
            referencedType = 'Letter'
            referencedEnd  = 'envelope'


    class String(model.PrimitiveType):
        def fromString(klass,value):
            return value
        fromString = classmethod(fromString)

    class Address(model.DataType):
    
        class name(model.structField):
            referencedType = 'String'

        class streetNumber(name):   pass
        class street(name):         pass
        class city(name):           pass
        class state(name):          pass
        class zip(name):            pass

        def __str__(self):
            return ", ".join(
                [self.name, '%s %s' % (self.streetNumber,self.street),
                    self.city, '%s %s' % (self.state, self.zip) ]
            )

MailText="""<?xml version="1.0"?>

<!--
    Example from the XMI 1.1 specification appendix

    Strangely, this example doesn't use XML namespaces to specify the
    metamodel; if it followed every other example of XMI 1.1 style, it
    would have a "Mail:" prefix on every content tag.  Ah well, so much
    for standards.
-->

<XMI version="1.1">

    <XMI.header>
        <XMI.model xmi.name="myMail" href="myMail.xml"/>
        <XMI.metamodel xmi.name="Mail" href="mail.xml"/>
    </XMI.header>

    <XMI.content>

        <Envelope xmi.id="myEnvelope" letter="myLetter">
        
            <Envelope.toAddress>
                <Address name="Sridhar" streetNumber="25725"
                    street="Jeronimo" city="Mission Viejo" state="CA" zip="92691"
                />
            </Envelope.toAddress>
            <Envelope.fromAddress>
                <Address name="Steve" streetNumber="555"
                    street="Bailey" city="San Jose" state="CA" zip="95141"
                />
            </Envelope.fromAddress>
                
        </Envelope>
        
        <Letter xmi.id="myLetter" envelope="myEnvelope"/>
        
    </XMI.content>

</XMI>"""

class XMIModelTests(TestCase):

    def setUp(self):
        model = MailModel()
        self.envelope, self.letter = model.importFromXMI(StringIO(MailText))

    def checkTypes(self):
        assert isinstance(self.envelope,MailModel.Envelope)
        assert isinstance(self.letter,MailModel.Letter)

    def checkLinks(self):
        assert self.envelope.letters == [self.letter]
        assert self.letter.envelope is self.envelope


    def checkAddresses(self):

        e = self.envelope

        assert str(e.toAddress)== \
            "Sridhar, 25725 Jeronimo, Mission Viejo, CA 92691"

        assert str(e.fromAddress)== \
            "Steve, 555 Bailey, San Jose, CA 95141"


















TestClasses = (
    XMIModelTests,
)


def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'check'))
    return TestSuite(s)

