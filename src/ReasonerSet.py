from src import *


class ReasonerSet (Object):

    """ set of reasoners """
    reasoners = []

    # initialize
    def __init__(self):
        self.detect_systems()


    def get_reasoners (self):
        return self.reasoners

    def detect_systems (self):
        """Read the active provers from the configuration file."""
#        self.provers_codes = {}
#        self.finders_codes = {}

        # local variables        
        provers = filemgt.read_config('active','provers').split(',')
        finders = filemgt.read_config('active','modelfinders').split(',')
        
        provers = [ s.strip() for s in provers ]
        finders = [ s.strip() for s in finders ]

        for prover in provers:
            r = Reasoner(prover)
            self.reasoners.append(r)
#            self.provers[prover] = None
        for finder in finders:
            r = Reasoner(finder, type=Reasoner.MODEL_FINDER)
            self.reasoners.append(r)
#            self.finders[finder] = None
        
        return True
      
      
    def construct_all_commands (self, modules, outfile_stem):
        for r in self.reasoners:
            r.construct_command(modules, outfile_stem)  
#
#    def construct_commands (self, modules, outfile_stem):
#        """construct the commands for all active provers and model finders."""
##        self.provers_codes = {}
##        self.finders_codes = {}
#        
#        for r in self.reasoners:
#            codes = commands.get_positive_returncodes(r)
#        
#        for prover in self.provers:
#            codes = commands.get_positive_returncodes(prover)
#            cmd = commands.get_system_command(prover, modules, outfile_stem)
#            self.provers[prover] = cmd
#            self.provers_codes[prover] = codes
#        for finder in self.finders:
#            codes = commands.get_positive_returncodes(finder)
#            cmd = commands.get_system_command(finder, modules, outfile_stem)
#            self.finders[finder] = cmd
#            self.finders_codes[finder] = codes
#        
#        return True
    
    def getProvers (self):
        provers = self.reasoners
        for p in provers:
            if not p.is_prover():
                provers.remove(p)
        return provers
    
    def getFinders (self):
        finders = self.reasoners
        for f in finders:
            if f.is_prover():
                finders.remove(f)
        return finders
    
#    def getCommand (self, name):
#        """Return the command for a given name of a prover or finder.  Assumes that names are unique, otherwise the prover is returned. 
#        If the name does not exist, returns None."""
#        value = self.provers.get(name)
#        if value:
#            return value
#        else:
#            return self.finders.get(name)

#    def getReturnCodes (self, name):
#        codes = self.provers_codes.get(name)
#        if codes:
#            return codes
#        else:
#            return self.finders_codes.get(name)