from peak.api import *
from interfaces import *
from peak.naming.factories.openable import FileURL
from html_doc import HTMLDocument





































class HTMLRunner(commands.AbstractCommand):

    usage="""Usage: peak ddt inputfile.html [outputfile.html]

Process the tests specified by the input file, sending an annotated version
to the output file, if specified, or to standard output if not specified.
Both the input and output files may be filenames or URLs.

A summary of the tests' pass/fail scores is output to stderr, and the command's
exitlevel is nonzero if there were any problems.
"""

    def DM(self):
        if len(self.argv)<2:
            raise commands.InvocationError("Input filename required")

        name = naming.toName(self.argv[1], FileURL.fromFilename)
        target = self.lookupComponent(name,adaptTo=naming.IStreamFactory)

        dm = HTMLDocument(self,
            text = target.open('b').read(), useAC = True,
        )

        if self.outputURL:
            dm.output = self.lookupComponent(
                self.outputURL,adaptTo=naming.IStreamFactory
            )
        else:
            dm.stream = self.stdout

        return dm

    DM = binding.Make(DM)

    def outputURL(self):
        if len(self.argv)>2:
            return naming.toName(self.argv[2], FileURL.fromFilename)

    outputURL = binding.Make(outputURL)


    def _run(self):

        dm = self.DM

        storage.beginTransaction(dm)

        summary = dm.document.summary
        summary['Input file'] = self.argv[1]
        if self.outputURL:
            summary['Output file'] = self.outputURL

        testZone = config.ServiceArea(self)     # tests happen in here
        processor = testZone.lookupComponent(IDocumentProcessor)
        processor.processDocument(dm.document)

        score = dm.document.score   # capture the final score
        dm.flush()                  # force DM to flush even if no changes made

        storage.commitTransaction(dm)

        print >>self.stderr,score   # Output scores to stderr
        return (score.wrong or score.exceptions) and 1 or 0



















