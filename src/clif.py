'''
Created on 2010-11-26
New module created on 2013-03-16

@author: Torsten Hahmann
'''
import os, logging, clif, filemgt

CLIF_IMPORT = 'cl-imports'

CLIF_COMMENT = 'cl-comment'

CLIF_MODULE = 'cl-module'

CLIF_TEXT = 'cl-text'

# CLIF symbols that are logically irrelevant
CLIF_OTHER_SYMBOLS = set([CLIF_IMPORT, CLIF_COMMENT, CLIF_MODULE, CLIF_TEXT])

# logical connectives in CLIF
CLIF_LOGICAL_CONNECTIVES = set(['not', 'and', 'or', 'iff', 'if', '=', 'exists', 'forall'])

TPTP_UNARY_SUBSTITUTIONS = {'not': '~'}

TPTP_NARY_SUBSTITUTIONS = {'and': '&', 'or': '|'}

TPTP_BINARY_SUBSTITUTIONS = {'=': '=', 'iff': '<=>', 'if': '=>'}

# CLIF quantifiers
TPTP_QUANTIFIER_SUBSTITUTIONS = {'forall':'!', 'exists':"?"}


def remove_all_comments(input_file, output_file):
    """Remove all comments (multi-line and single-line comments), including cl-comment blocks from the given CLIF file.
    Parameters:
    input_file -- filename of the CLIF input
    output_file -- filename where to write the CLIF file removed of comments."""
               
    def strip_sections (lines, begin_symbol, end_symbol):           
        """Remove sections that start with the begin_symbol and end with end_symbol"""
        output = []
        if len(lines)==0: return output
        line = lines.pop(0)
        within_section = False  # variable to denote that we are currently within a multiline section
        outline = ""
        start = ""
        while True:
            if within_section and end_symbol not in line:
                # ignore line: do not write to output
                if len(output)>0:
                    output.append(outline)
                outline = ""
                if len(lines)>0: line = lines.pop(0)
                else:
                    output.append(start) 
                    raise ClifParsingError('Syntax error in clif input: no matching' + end_symbol + ' for ' + begin_symbol + ' on line ' + str(len(output)+1),output)                    
            elif within_section and end_symbol in line:
                within_section = False
                # normally process the remainder 
                line = line.split(end_symbol,1)
                if len(line)>0:
                    line=line[1]
            elif not within_section and begin_symbol in line:
                within_section = True
                line = line.split(begin_symbol,1)
                start = line[0]
                outline = line[0] + '\n'
                if len(line[1])>1:
                    line = line[1]
            else:
                # copy line to output
                outline += line
                output.append(outline)
                outline = ""
                if len(lines)>0: line = lines.pop(0)
                else: return output        
    
    def strip_clif_comments (lines):
        output = []
        if len(lines)==0: return output
        line = lines.pop(0)
        outline = ""
        search_end = False
        start = ""
        while True:
            if search_end:
                # searching for the closing quotes
                line = line.split('\'',1)
                if len(line)>1:
                    # closing quotes found in line
                    search_end = False
                    line = line[1].split(')',1)
                    if len(line)<2:
                        output.append(start) 
                        raise ClifParsingError('Syntax error in clif input: no closing parenthesis found for ' + CLIF_COMMENT + ' on line ' + str(len(output)+1),output)                    
                    if len(line[0].strip())>0:
                        output.append(start) 
                        raise ClifParsingError('Syntax error in clif input: found illegal characters before closing parenthesis in ' + CLIF_COMMENT + ' on line ' + str(len(output)+1),output)
                    outline += line[1]
                    output.append(outline)
                    outline = ""
                    if len(lines)>0: line = lines.pop(0)
                    else: return output                        
                else:
                    # no closing quotes found in line, proceed to next line
                    outline = ""
                    if len(lines)>0: line = lines.pop(0)
                    else:
                        output.append(start) 
                        raise ClifParsingError('Syntax error in clif input: missing closing quotes for ' + CLIF_COMMENT + ' on line ' + str(len(output)+1),output)                    
            elif CLIF_COMMENT not in line:
                # just copy the line to output
                outline += line
                output.append(outline)
                outline = ""
                if len(lines)>0: line = lines.pop(0)
                else: return output        
            else: 
                # found a cl-comment
                parts = line.split(CLIF_COMMENT,1)
                parts2 = parts[0].rsplit('(',1)
                start = line
                if len(parts2)<2:
                    output.append(start) 
                    raise ClifParsingError('Syntax error in clif input: no opening parenthesis found before ' + CLIF_COMMENT + ' on line ' + str(len(output)+1),output)                    
                search = True
                if len(parts[0].strip())>1: 
                    output.append(parts[0][0:-1] + '\n')
                # searching for the begin of the comment quotes
                line = parts[1].split('\'',1)
                if len(line[0].strip())>0: 
                    output.append(start) 
                    raise ClifParsingError('Syntax error in clif input: found illegal characters after ' + CLIF_COMMENT + ' on line ' + str(len(output)+1),output)      
                line = line[1]
                search_end = True

    
    def strip_lines (lines, begin_symbol):
        """Remove comments that start with begin_symbol."""
        output = []
        for line in lines:
            newline = line.split(begin_symbol,1)[0]
            if len(newline)<len(line):
                output.append(newline + '\n')
            else:
                output.append(newline)            
        return output

    # MAIN METHOD remove_all_comments()
    lines = []

    with open(input_file, 'r') as file:
        try:
            lines = file.readlines()
            #print lines
            # DO stuff
            lines = strip_sections(lines, '/*', '*/')
            lines = strip_clif_comments(lines)
            lines = strip_lines(lines,'//')
        except IOError:
            file.close()
        except ClifParsingError as e:
            logging.getLogger(__name__).error(e)
            file.close()
            lines = []
        finally:
            file.close()

    with open(output_file, 'w+') as file:
        logging.getLogger(__name__).debug("Writing to " + os.path.abspath(output_file))
        try:
            file.writelines(lines)
        except IOError:
            file.close()
        finally:
            file.close()

def reformat_urls(lines):
    """Delete URL prefixes from all import declarations.""" 
    lines = list(lines)
    prefixes = filemgt.read_config('cl','prefix').split(',')
    prefixes = [p.strip().strip('"') for p in prefixes]
    prefixes = sorted([p.strip() for p in prefixes], key=lambda s: len(s), reverse=True) 
    for i in range(0,len(lines)):
        for prefix in prefixes:
            lines[i] = lines[i].replace(prefix,'')
            lines[i] = lines[i].strip('/')
            #print lines[i]
    return lines

                

def get_all_nonlogical_symbols (filename):
    nonlogical_symbols = set([])
    sentences = clif.get_sentences_from_file(filename)
    for sentence in sentences:
        #print "SENTENCE = " + sentence
        nonlogical_symbols.update(clif.get_nonlogical_symbols(sentence))
    logging.getLogger(__name__).debug("Nonlogical symbols: " + str(nonlogical_symbols))
    return nonlogical_symbols


def get_sentences_from_file (input_file_name):
        """ extract all Clif sentences from a Clif input file and returns the sentences as a list of strings."""
        cl_file = open(input_file_name, 'r')
        text = cl_file.readlines()
        cl_file.close()
        text = "".join(text)    # compile into a single string
        quantified_terms = clif.get_quantified_terms(text)
        return clif.get_sentences(quantified_terms)
    

def get_quantified_terms (text):
    """Extracts all quantified terms from a string that contains the content of a CLIF file"""
    text = text.replace("\t","")   # remove tabs
    text = text.replace("\n","")   # remove linebreaks
    pieces = [text]
    for q in clif.TPTP_QUANTIFIER_SUBSTITUTIONS.keys():
        old_pieces = pieces
        pieces = [p.split(q) for p in old_pieces]
        new_pieces = []
        for i in range(0,len(pieces)):
            if len(pieces[i])==1:
                new_pieces.append(old_pieces[i])
            else:
                new_pieces.append(pieces[i].pop(0)) # copy the first one as-is
                new_pieces.extend(['(' + q + ' ' + p.strip() for p in pieces[i]])
        pieces = new_pieces
        for i in range(0,len(pieces)-1):
            #print pieces[i]
            if pieces[i].endswith("("):
                pieces[i] = pieces[i][:-1]  # remove last character, the opening parenthesis

    pieces.pop(0)   # delete non-relevant part
    return pieces


def get_sentences (quantified_terms):
    """Reconstruct the sentences from a list of quantified terms in CLIF notation by matching parentheses.
    Returns a set of strings, each is a logical sentence surrounded by parentheses."""
    new_pieces = []
    pieces = quantified_terms
    #print pieces
    for i in range (0,len(pieces)):
        #print pieces[i]
        open_parentheses = pieces[i].count('(') - pieces[i].count(')')
        if i==len(pieces)-1:
            #print "last piece, removing parentheses " + str(open_parentheses)
            for n in range(0,open_parentheses):
                pieces[i] = pieces[i].rsplit(')',1)[0]
            new_pieces.append(pieces[i])
        elif open_parentheses == 0:
            #print pieces[i]
            new_pieces.append(pieces[i])  # end of quantified term
        else:
            pieces[i+1] = pieces[i] + pieces[i+1]
    return new_pieces
              

def get_variables (sentence):
    """Extract the variables from a logical sentence in CLIF notation."""
    variables = set([])
    pieces = [sentence[1:-1].strip()] # crop outer parentheses
    for q in clif.TPTP_QUANTIFIER_SUBSTITUTIONS.keys():
        pieces = [p.split(q) for p in pieces]
        pieces = [p.strip() for sublist in pieces for p in sublist]   # flatten list
    pieces = set(pieces)
    pieces.discard('')
    #print pieces
    for p in pieces:
        new_vars = p.split('(',1)[1].split(')',1)[0].split()
        variables.update(new_vars)
    #print variables
    return variables

def get_nonlogical_symbols_and_variables (sentence):
    """Extract all nonlogical symbols and variables from a logical sentence in CLIF notation."""
    variables = clif.get_variables(sentence)

    pieces = sentence.split()
    pieces = [p.split('(') for p in pieces]
    pieces = [item for sublist in pieces for item in sublist] # flatten list
    pieces = [p.split(')') for p in pieces]
    pieces = [item for sublist in pieces for item in sublist] # flatten list
    pieces = [p.strip() for p in pieces]
    #print "removing variables " + str(variables) 
    pieces = set(pieces) - set(clif.CLIF_LOGICAL_CONNECTIVES) - set(clif.CLIF_OTHER_SYMBOLS) -set(['']) - set(variables)
    return (pieces, variables)


def get_nonlogical_symbols (sentence):
    """Extract all nonlogical symbols from a logical sentence in CLIF notation."""
    (_, non_logical_symbols) = clif.get_nonlogical_symbols_and_variables (sentence)
    return non_logical_symbols



def to_tptp (input_file_names):
    """Translates a set of Clif files to TPTP syntax.
    All sentences are treated as FOL sentences in the segregated dialect of CLIF.
    Quantifying over relations or functions is currently not supported.
    All nonlogical symbols are converted to lowercase. 
    Nonlogical symbols that start with non-alphabetic characters are automatically replaced by symbols clifsymbN.
    """
    
    sentences = []
    for file_name in input_file_names:
        sentences.extend(clif.get_sentences_from_file(file_name))
    #variables_dict = {s: None for s in sentences}
    #nonlogical_dict = variables_dict.copy()
    variables_list = []
    nonlogical_list = []
    # obtain variables and nonlogical symbols for each sentence
    for sentence in sentences:
        (nonlogical_symbols, variables) = clif.get_nonlogical_symbols_and_variables (sentence)
        variables_list.append(variables)
        nonlogical_list.append(nonlogical_symbols)
    
    if len(variables_list)>0:
        max_vars = min(1,max([len(v) for v in variables_list]))
    else:
        max_vars = 1        
    import math
    digits = int(math.ceil((math.log10(max_vars))))
    #print "Max number of variables = " + str(max_vars)
    #print "Digits = " + str(digits)
    
    #automatic replacement symbols
    auto_number = 1
    auto_dict = {}
    all_nonlogical_symbols = set([s for list in nonlogical_list for s in list])
    for s in all_nonlogical_symbols:
        if not s[0].isalpha():
            auto_dict[s] = 'clifsym' + str(auto_number)
            auto_number += 1 

    auto_keys =  auto_dict.keys()
    auto_keys.sort(key=lambda s: len(s), reverse=True)   
    #print str(auto_keys)
    
    # translate sentences
    tptp_sentences = []
#    for i in range(0, 1):
    for i in range(0, len(sentences)):
        print str(int((i+1)*math.pow(10,digits))) + " " + str(sentences[i]) + " VARS = " + str(variables_list[i]) + " SYMBOLS = " + str(nonlogical_list[i])
        translation = sentence_to_tptp(sentences[i], nonlogical_list[i], variables_list[i], int((i+1)*math.pow(10,digits)), axiom=True)
        # replace non-standard symbols
        for s in auto_keys:
            translation = translation.replace('"' +s.lower() +'"', '"'+auto_dict.get(s)+'"')
            #print translation       
        tptp_sentences.append(translation)
        
    return [t.replace('"','') for t in tptp_sentences]
    


def sentence_to_tptp (sentence, nonlogical_symbols, variables, sentence_number, axiom=True):
    """Translate a single sentence to TPTP format and assign it the the sentence_number.
    In the translation every nonlogical symbol is replaced and variables are numbered starting with start_number.
    Parameters:
    nonlogical_symbols -- dictionary of the nonlogical symbols and their replacement, sorted by length in decreasing order
    variables -- list of all quantified variables in this sentence, sorted by length in decreasing order
    sentence_number -- number to assign this sentence; must be a number 10^n with n>1 depending on the maximal 
                       numbers of distinct variables in a single sentence in the translation.
    axiom -- indicates whether this is an axiom (True) or a lemma (or conjecture, False)   
    assume nonlogical_symbols are sorted by length in decreasing order
    """
    
    def replace_logical_connectives (pieces):
    
        #print "INCOMING SENTENCE = " + str(pieces)

        # base case
        if not isinstance(pieces,list):
            #print "DONE: " + str(pieces)
            return pieces

        while '' in pieces:
            pieces.remove('')

        if len(pieces)==1:
            return replace_logical_connectives(pieces[0])
                
        # special case: quantifiers; need to treat the second argument separate
        for quantifier in TPTP_QUANTIFIER_SUBSTITUTIONS.keys():
            if quantifier==pieces[0].strip().strip('(').strip():
                if len(pieces)>3:
                    # ensure it is really used in a binary way
                    raise ClifParsingError("wrong use of quantifier '" + quantifier + "' in term '" + str(pieces) + "'"  )
                sentence = "( "
                for var in pieces[1]:
                    sentence += TPTP_QUANTIFIER_SUBSTITUTIONS[quantifier] + " [" + var + "] : "
                #print "QUANTIFIER REMAINDER: " + str(pieces[2])
                remainder = replace_logical_connectives(pieces[2])
                #print "QUANTIFIER REMAINDER: " + str(remainder)
                sentence += remainder + ") "  
                return sentence
        
        # recursion otherwise
        for i in range(0,len(pieces)):
            replacement = replace_logical_connectives(pieces[i])
            if replacement is None:
                raise ClifParsingError("could not parse: " + str(pieces[i]) + "")
            pieces[i] = replacement
            #print "RETURNING: " +  pieces[i]
        
        
        if len(pieces)==2:
            #sentence = pieces[0].strip('(').strip(')')
            # substitute unary connectives
            for connective in TPTP_UNARY_SUBSTITUTIONS.keys():
                if connective==pieces[0].strip().strip('(').strip():
                    pieces[0] = pieces[0].replace(connective, TPTP_UNARY_SUBSTITUTIONS[connective] + " ")
                    sentence = "(" + pieces[0] + pieces[1] + ")"
                    #print "UNARY: " + sentence
                    return sentence
            
        
        for connective in TPTP_BINARY_SUBSTITUTIONS.keys():
            if connective==pieces[0].strip().strip('(').strip():
                if len(pieces)>3:
                    # ensure it is really used in a binary way
                    raise ClifParsingError("wrong use of logical connective '" + connective + "' in term '" + str(pieces) + "'"  )
                sentence = ("( (" + pieces[1] + ") " + 
                             TPTP_BINARY_SUBSTITUTIONS[connective] + 
                             " (" + pieces[2] + ") )")
                #print "BINARY: " + sentence
                return sentence
        
        for connective in TPTP_NARY_SUBSTITUTIONS.keys():
            if connective==pieces[0].strip().strip('(').strip():
                sentence = "(" + pieces[1]
                for i in range(2,len(pieces)):
                    sentence += " " + TPTP_NARY_SUBSTITUTIONS[connective] + " " + pieces[i]
                sentence +=  ")"
                #print "NARY: " +  sentence
                return sentence

        print "PROCESSING SYMBOLS: " + str(pieces)
                
        for symbol in nonlogical_symbols:
            if symbol.lower()==pieces[0].strip().strip('(').strip().strip('"'):
                sentence = '"'+symbol.lower()+'"' + "(" + pieces[1]
                for i in range(2,len(pieces)):
                    sentence += ", " + pieces[i]
                sentence += ")"
                print "DONE: " + sentence
                return sentence 
        
            
    # END OF replace_logical_connectives

    tptp_sentence = "fof(sos"
    tptp_sentence += str(sentence_number) +","
    if axiom:
        tptp_sentence += "axiom,"
    else:
        tptp_sentence += "conjecture,"
    
    # join nonlogical symbols and variables and sort them decreasingly by length
    replaced_symbols = nonlogical_symbols
    replaced_symbols.update(variables)
    replaced_symbols = list(replaced_symbols)
    #replaced_symbols = [p.lower() for p in replaced_symbols]
    replaced_symbols.sort(key=lambda s: len(s), reverse=True)

    # update keys of non_logical symobls to all upper case
    #upper_nonlogical_symbols = [s.lower() for s in nonlogical_symbols]
    var_no = 1
    
    for i in range(0, len(replaced_symbols)):
        s = replaced_symbols[i] 
        #print "replacing " + s
        if s in variables:
            #print str(sentence_number + var_no)
            sentence = sentence.replace('('+s+')','("X'+str(sentence_number + var_no)+'")')
            sentence = sentence.replace('('+s+' ','("X'+str(sentence_number + var_no)+'" ')
            sentence = sentence.replace(' '+s+')',' "X'+str(sentence_number + var_no)+'")')
            sentence = sentence.replace(' '+s+' ',' "X'+str(sentence_number + var_no)+'" ')
            var_no += 1
        else:
            sentence = sentence.replace('('+s+')','("'+s.lower()+'")')
            sentence = sentence.replace('('+s+' ','("'+s.lower()+'" ')
            sentence = sentence.replace(' '+s+')',' "'+s.lower()+'")')
            sentence = sentence.replace(' '+s+' ',' "'+s.lower()+'" ')

    from pyparsing import nestedExpr   
    pieces = nestedExpr('(',')').parseString(sentence).asList()

    sentence = replace_logical_connectives(pieces)
    #sentence = quantifiers_to_tptp(sentence)
    sentence = sentence.replace("'","")
    tptp_sentence = tptp_sentence + sentence
    tptp_sentence += ")."
    #print "TPTP: " + tptp_sentence
    return tptp_sentence

         



def get_variables (sentence):
    """Extract the variables from a logical sentence in CLIF notation."""
    variables = set([])
    pieces = [sentence[1:-1].strip()] # crop outer parentheses
    for q in clif.TPTP_QUANTIFIER_SUBSTITUTIONS.keys():
        pieces = [p.split(q) for p in pieces]
        pieces = [p.strip() for sublist in pieces for p in sublist]   # flatten list
    pieces = set(pieces)
    pieces.discard('')
    #print pieces
    for p in pieces:
        new_vars = p.split('(',1)[1].split(')',1)[0].split()
        variables.update(new_vars)
    #print variables
    return variables


def get_imports(input_file):
    """Find all the imported modules from a CLIF file.
    Parameters:
    input_file -- filename of the CLIF input."""

    imports = set([])
    
    cl_file = open(input_file, 'r')
    text = "".join(cl_file.readlines())
    #print text
    cl_file.close()

    text = text.split(clif.CLIF_IMPORT)
    for i in range(1,len(text)):
        line = text[i].split(")",1) # find first closing parenthesis
        imports.add(line[0].strip())
    imports = reformat_urls(imports)
    #print imports
    return imports



class ClifParsingError(Exception):
    
    output = []
    
    def __init__(self, value, output=[]):
        self.value = value
        self.output = output
    def __str__(self):
        return repr(self.value) + '\n\n' + (''.join('{}: {}'.format(*k) for k in enumerate(self.output)))

    
if __name__ == '__main__':
    import sys
    # global variables
    options = sys.argv
    remove_all_comments(options[1], options[2])

