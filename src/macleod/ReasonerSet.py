import macleod.Filemgt
import macleod.Reasoner

import logging

class ReasonerSet (list):  
    """ list of reasoners """

    # initialize
    def __init__(self):
        list.__init__(self)
        self.detect_systems()

    def detect_systems (self):
        """Read the active provers from the configuration file."""

        # local variables        
        provers = macleod.Filemgt.read_config('active','provers').split(',')
        finders = macleod.Filemgt.read_config('active','modelfinders').split(',')

        provers = [ s.strip() for s in provers ]
        finders = [ s.strip() for s in finders ]

        provers = [x for x in provers if len(x)>0]
        finders = [x for x in finders if len(x)>0]

        self.extend([macleod.Reasoner.Reasoner(r) for r in provers])
        self.extend([macleod.Reasoner.Reasoner(r, reasoner_type=macleod.Reasoner.Reasoner.MODEL_FINDER) for r in finders])

        logging.getLogger(__name__).debug("REASONER SET: " + str(provers+finders))

        return True


    def constructAllCommands (self, ontology):
        for r in self:
            r.constructCommand(ontology)

    def getByName (self, name):
        for i in range(0,len(self)):
            if self[i].name == name: return self[i]
        return None

    def getByCommand (self, command):
        for i in range(0,len(self)):
            if self[i].args[0] == command: return self[i]
        return None


    def getProvers (self):
        provers = self
        for p in provers:
            if not p.isProver():
                provers.remove(p)
        return provers

    def getFinders (self):
        finders = self
        for f in finders:
            if f.isProver():
                finders.remove(f)
        return finders
