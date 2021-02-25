import macleod
import macleod.Commands
import macleod.Filemgt
import logging


class Reasoner (object):

    MODEL_FINDER = 'MODEL_FINDER'

    PROVER = 'PROVER'

    # initialize
    def __init__(self, name, reasoner_type=None, reasoner_id=None):
        
        logging.getLogger(__name__).debug('Initializing ' + name)

        self.identifier = ''

        self.type = Reasoner.PROVER

        self.args = []

        self.input_files = ''

        self.output_file = ''

        self.ontology = ''

        self.time = -1

        self.output = None

        self.name = name

        if reasoner_type:
            self.type = reasoner_type
        if reasoner_id:
            self.identifier = reasoner_id
        else:
            self.identifier = name

        self.timeout = macleod.Filemgt.read_config(self.name,'timeout')
        
        logging.getLogger(__name__).debug('Finished initializing ' + name)
        

    def getId (self):
        return self.identifier
        
    def __eq__ (self, other):
        if not isinstance(other, Reasoner):
            return False
        if self.identifier == other.identifier:
            return True
        else:
            return False

    def __ne__ (self, other):
        return not self.eq(other)

    def constructCommand (self, ontology):
        import os
        """Return the command (includes constructing it if necessary) to invoke the reasoner."""
        self.args = macleod.Commands.get_system_command(self.name, ontology)

        self.ontology = ontology
        self.output_file = ontology.get_output_filename(self.name, out=True)
        logging.getLogger(__name__).info(self.name + " writes output to " + self.output_file)

        logging.getLogger(__name__).debug('Reasoner command: ' + str(self.args))
        return self.args

    def getCommand (self):
        return self.args

    def getOutputFile (self):
        return self.output_file

    def getOntology (self):
        return self.ontology

    def isProver (self):
        if self.type==Reasoner.PROVER: return True
        else: return False

    def terminatedSuccessfully (self):
        mapping = {
            macleod.Ontology.PROOF: True,
            macleod.Ontology.COUNTEREXAMPLE: True,
            macleod.Ontology.CONSISTENT: True,
            macleod.Ontology.INCONSISTENT: True,
            macleod.Ontology.ERROR : False,
            macleod.Ontology.UNKNOWN : False,
            None: False
        }

        def paradox_status(line):
            if 'Theorem' in line:
                #print "PARADOX SZS status found: THEOREM"
                return macleod.Ontology.PROOF
            elif 'Unsatisfiable' in line:
                return macleod.Ontology.INCONSISTENT
            elif 'CounterSatisfiable' in line:
                return macleod.Ontology.COUNTEREXAMPLE
            elif 'Satisfiable' in line:
                return macleod.Ontology.CONSISTENT
            else: # Timeout, GaveUp
                return macleod.Ontology.UNKNOWN

        def vampire_status(line):
            if 'Refutation not found' in line:
                return macleod.Ontology.UNKNOWN
            elif 'Refutation' in line:
                #print "VAMPIRE SZS status found: THEOREM"
                return macleod.Ontology.PROOF
            elif 'Unsatisfiable' in line:
                return macleod.Ontology.INCONSISTENT
            elif 'CounterSatisfiable' in line:
                return macleod.Ontology.COUNTEREXAMPLE
            elif 'Satisfiable' in line:
                return macleod.Ontology.CONSISTENT
            else: # Timeout, GaveUp
                return macleod.Ontology.UNKNOWN

        def success_default (self):
            return False

        def success_prover9 (self):
            out_file = open(self.output_file, 'r')
            lines = out_file.readlines()
            out_file.close()
            output_lines = [x for x in lines if x.startswith('THEOREM PROVED')]
            if len(output_lines)>0:
                self.output = macleod.Ontology.PROOF

            return mapping[self.output]



        def success_vampire (self):
            out_file = open(self.output_file, 'r')
            lines = out_file.readlines()
            out_file.close()
            output_lines = [x for x in lines if x.startswith('% Termination reason:')]
            l = len(output_lines)
            if l==0:
                self.output = macleod.Ontology.UNKNOWN
            # at least one line has a termination reason, so this might be an intermediate line (since Vampire in competition mode restarts several times)
            else:
                # examine the last output line
                self.output = vampire_status(output_lines[l-1])
                if self.output == macleod.Ontology.UNKNOWN:
                    # Handle exceptions during parsing
                    #print(str(lines))
                    output_lines = [x for x in lines if x.startswith('Parser exception:')]
                    if len(output_lines)>0:
                        self.output = macleod.Ontology.ERROR

            return mapping[self.output]


        def success_paradox (self):
            out_file = open(self.output_file, 'r')
            lines = out_file.readlines()
            out_file.close()
            output_lines = [x for x in lines if x.startswith('+++ RESULT:')]
            if len(output_lines)!=1:
                output_lines = [x for x in lines if x.startswith('*** Unexpected:')]
                #print(str(lines))
                if len(output_lines)>0:
                    self.output = macleod.Ontology.ERROR
                else:
                    self.output = macleod.Ontology.UNKNOWN
            else:
                self.output = paradox_status(output_lines[0])
                #logging.getLogger(self.__module__ + "." + self.__class__.__name__).debug('Paradox terminated successfully : ' + str(self.output))

            return mapping[self.output]

        def success_mace4 (self):
            out_file = open(self.output_file, 'r')
            lines = out_file.readlines()
            out_file.close()
            output_lines = [x for x in lines if x.startswith('Exiting with 1 model.')]
            if len(output_lines)==0:
                self.output = macleod.Ontology.UNKNOWN
            else:
                self.output = macleod.Ontology.CONSISTENT
                self.output = macleod.Ontology.CONSISTENT

            return mapping[self.output]


        handlers = {
            "mace4": success_mace4,
            "prover9": success_prover9,
            "paradox": success_paradox,
            "vampire": success_vampire,
        }

        return handlers.get(self.name, success_default)(self)

    def terminatedWithError (self):
        # need to involve terminatedSuccessfully to make sure the self.output is set
        self.terminatedSuccessfully()

        if self.output==macleod.Ontology.ERROR:
            return True
        else:
            return False

    def terminatedUnknowingly (self):
        return not(self.terminatedSuccessfully()) and not(self.terminatedWithError())

    def isDone (self):
        if self.output is None:
            return False
        else:
            return True
