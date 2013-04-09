from src import *

class Reasoner (object):
    
    MODEL_FINDER = 'MODEL_FINDER'
    
    PROVER = 'PROVER'
        
    # initialize
    def __init__(self, name, type=None, id=None):
        self.identifier = ''
        
        self.type = Reasoner.PROVER
        
        self.args = []
        
        self.positive_returncodes = []
        
        self.unknown_returncodes = []
        
        self.modules = []
        
        self.output_file = ''
        
        self.return_code = None
        
        self.output = None

        self.name = name
        if type:
            self.type = type
        if id:
            self.identifier = id
        else:
            self.identifier = name
        self.positive_returncodes = commands.get_positive_returncodes(self.name)
        self.unknown_returncodes = commands.get_unknown_returncodes(self.name)


    def __eq__ (self, other):
        if not isinstance(other, Reasoner):
            return False
        if self.identifier == other.identifier:
            return True
        else:
            return False
        
    def __ne__ (self, other):
        return not self.eq(other)

    def constructCommand (self, modules, outfile_stem):
        """Construct the command to invoke the reasoner."""
        self.modules = modules
        self.output_file = outfile_stem + filemgt.read_config(self.name,'ending')
        self.args = commands.get_system_command(self.name, self.modules, self.output_file)
        return self.args
    
    def getCommand (self, modules=None, outfile_stem=None):
        """Return the command (includes constructing it if necessary) to invoke the reasoner."""
        if not modules:
            return self.args
        else:
            self.construct_command(modules, outfile_stem)
            return self.args
    
    def getOutfile(self):
        return self.output_file        

    def isProver (self):
        if self.type==Reasoner.PROVER: return True
        else: return False
        
    def terminatedSuccessfully (self):
        from src import ClifModuleSet
    
        def success_default (self):
            if not self.return_code==None:
                if self.return_code in self.positive_returncodes:
                    if self.isProver():
                        self.output = ClifModuleSet.PROOF
                    else:
                        self.output = ClifModuleSet.CONSISTENT
                    return True
            return False

        def success_paradox (self):
            file = open(self.output_file, 'r')
            lines = file.readlines()
            output_lines = filter(lambda x: x.startswith('+++ RESULT:'), lines)
            if len(output_lines)!=1:
                if not self.return_code:
                    self.output = None
                else:
                    self.output = ClifModuleSet.UNKNOWN                    
            else:
                if 'Theorem' in output_lines[0]:
                    self.output = ClifModuleSet.PROOF
                elif 'CounterSatisfiable' in output_lines[0]:
                    self.output = ClifModuleSet.INCONSISTENT
                elif 'Unsatisfiable' in output_lines[0]:
                    self.output = ClifModuleSet.INCONSISTENT
                elif 'Satisfiable' in output_lines[0]:
                    self.output = ClifModuleSet.CONSISTENT
                else:
                    self.output = ClifModuleSet.UNKNOWN
            
            mapping = {
                ClifModuleSet.CONSISTENT: True,
                ClifModuleSet.INCONSISTENT : True,
                ClifModuleSet.UNKNOWN : False,
                None: False
            }
            
            return mapping[self.output]
        
    
        handlers = {
            "paradox": success_paradox, 
        }
    
        return handlers.get(self.name, success_default)(self)
     
     
    def terminatedUnknowingly (self):
        from src import ClifModuleSet

        def unknown_default (self):
            if not self.return_code==None:
                if self.return_code in self.unknown_returncodes:
                    self.output = ClifModuleSet.UNKNOWN
                    return True
            return False
        
        def unknown_paradox (self):
            success = self.terminatedSuccessfully()
            if success:
                return False
            elif self.return_code==None:
                return False
            else: 
                return True

        
        handlers = {
            "paradox": unknown_paradox, 
        }
            
        return handlers.get(self.name, unknown_default)(self)
        
        
    def setReturnCode(self, rc):
        self.return_code = rc
                
    def isDone (self):
        if self.output is None:
            return False
        else:
            return True
