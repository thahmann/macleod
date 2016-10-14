from macleod import filemgt, commands
import logging

class Reasoner (object):

    MODEL_FINDER = 'MODEL_FINDER'

    PROVER = 'PROVER'

    # initialize
    def __init__(self, name, reasoner_type=None, reasoner_id=None):
        self.identifier = ''

        self.type = Reasoner.PROVER

        self.args = []

        self.positive_returncodes = []

        self.unknown_returncodes = []

        self.modules = []

        self.input_files = ''

        self.output_file = ''

        self.time = -1

        self.return_code = None

        self.output = None

        self.name = name
        if reasoner_type:
            self.type = reasoner_type
        if reasoner_id:
            self.identifier = reasoner_id
        else:
            self.identifier = name
        self.positive_returncodes = commands.get_positive_returncodes(self.name)
        self.unknown_returncodes = commands.get_unknown_returncodes(self.name)

        self.timeout = filemgt.read_config(self.name,'timeout')

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
        (self.args, self.input_files) = commands.get_system_command(self.name, modules, self.output_file)
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

    def getInputFiles (self):
        return self.input_files

    def isProver (self):
        if self.type==Reasoner.PROVER: return True
        else: return False

    def terminatedSuccessfully (self):
        from macleod.ClifModuleSet import ClifModuleSet
        mapping = {
            ClifModuleSet.CONSISTENT: True,
            ClifModuleSet.INCONSISTENT : True,
            ClifModuleSet.UNKNOWN : False,
            None: False
        }

        def szs_status(line):
            if 'Theorem' in line:
                #print "VAMPIRE SZS status found: THEOREM"
                return ClifModuleSet.PROOF
            elif 'Unsatisfiable' in line:
                return ClifModuleSet.INCONSISTENT
            elif 'CounterSatisfiable' in line:
                return ClifModuleSet.COUNTEREXAMPLE
            elif 'Satisfiable' in line:
                return ClifModuleSet.CONSISTENT
            else: # Timeout, GaveUp, Error
                return ClifModuleSet.UNKNOWN

        def success_default (self):
            if not self.return_code==None:
                if self.return_code in self.positive_returncodes:
                    if self.isProver():
                        self.output = ClifModuleSet.PROOF
                    else:
                        self.output = ClifModuleSet.CONSISTENT
                    return True
            return False

        def success_vampire (self):
            out_file = open(self.output_file, 'r')
            lines = out_file.readlines()
            out_file.close()
            output_lines = [x for x in lines if x.startswith('% SZS status')]
            if len(output_lines)!=1:
                if not self.return_code:
                    self.output = None
                else:
                    self.output = ClifModuleSet.UNKNOWN                    
            else:
                self.output = szs_status(output_lines[0])

            return mapping[self.output]


        def success_paradox (self):
            out_file = open(self.output_file, 'r')
            lines = out_file.readlines()
            out_file.close()
            output_lines = [x for x in lines if x.startswith('+++ RESULT:')]
            if len(output_lines)!=1:
                if not self.return_code:
                    self.output = None
                else:
                    self.output = ClifModuleSet.UNKNOWN                    
            else:
                self.output = szs_status(output_lines[0])
                logging.getLogger(self.__module__ + "." + self.__class__.__name__).debug('Paradox terminated successfully : ' + str(self.output))


            return mapping[self.output]


        handlers = {
            "paradox": success_paradox, 
            "vampire": success_vampire, 
        }

        return handlers.get(self.name, success_default)(self)


    def terminatedUnknowingly (self):
        from macleod.ClifModuleSet import ClifModuleSet

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
