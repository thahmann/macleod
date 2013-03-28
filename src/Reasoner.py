from src import *

class Reasoner (object):
    
    MODEL_FINDER = 'MODEL_FINDER'
    
    PROVER = 'PROVER'
    
    identifier = ''
    
    name = ''
    
    type = PROVER
    
    command = ''
    
    positive_returncodes = []
    
    unknown_returncodes = []
    
    modules = []
    
    outfile_stem = ''
    
    return_code = None
    
    # initialize
    def __init__(self, name, type=None, id=None):
        self.name = name
        if type:
            self.type = type
        if id:
            self.identifier = id
        else:
            self.identifier = name
        self.positive_returncodes = commands.get_positive_returncodes(self.name)
        self.unknown_returncodes = commands.get_unknown_returncodes(self.name)
        self.return_code = None

    def __eq__ (self, other):
        if not isinstance(other, Reasoner):
            return false
        if self.identifier == other.identifier:
            return true
        else:
            return false
        
    def __ne__ (self, other):
        return not self.eq(other)

    def constructCommand (self, modules, outfile_stem):
        """Construct the command to invoke the reasoner."""
        self.modules = modules
        self.outfile_stem = outfile_stem
        self.command = commands.get_system_command(self.name, self.modules, self.outfile_stem)
        return self.command
    
    def getCommand (self, modules=None, outfile_stem=None):
        """Return the command (includes constructing it if necessary) to invoke the reasoner."""
        if not modules:
            return self.command
        else:
            return self.construct_command(modules, outfile_stem)

    def isProver (self):
        if self.type==Reasoner.PROVER: return True
        else: return False
        
    def terminatedSuccessfully (self):
        if self.return_code:
            if self.return_code in self.positive_returncodes:
                return true
        return false
            
    def terminatedUnknowingly (self):
        if self.return_code:
            if self.return_code in self.unknown_returncodes:
                return true
        return false
        
            
    def isDone (self):
        return self.return_code