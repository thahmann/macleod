'''
Created on 2010-11-26
New module created on 2013-03-16

@author: Torsten Hahmann
'''
import os, logging, clif, filemgt

# logical connectives in CLIF
CLIF_LOGICAL_CONNECTIVES = set(['not', 'and', 'or', 'iff', 'if', 'exists', 'forall', '='])
# CLIF symbols that are logically irrelevant
CLIF_OTHER_SYMBOLS = set(['cl-text', 'cl-module', 'cl-imports'])
# CLIF quantifiers
CLIF_QUANTIFIERS = set(['forall', 'exists'])

CLIF_IMPORT = 'cl-imports'

CLIF_COMMENT = 'cl-comment'


def remove_all_comments(input_file, output_file):
    """Remove all comments (multi-line and single-line comments), including cl-comment blocks from the given CLIF file.
    Parameters:
    input_file -- filename of the CLIF input
    output_file -- filename where to write the CLIF file removed of comments."""

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
    """Delete URL prefixes from all imports declarations.""" 
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



def strip_lines (lines, begin_symbol):
    """Remove comments that start with begin_symbol"""
    output = []
    for line in lines:
        newline = line.split(begin_symbol,1)[0]
        if len(newline)<len(line):
            output.append(newline + '\n')
        else:
            output.append(newline)            
    return output


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
            

def get_quantified_terms(text):
    """Extracts all quantified terms from a string that contains the content of a CLIF file"""
    text = text.replace("\t","")   # remove tabs
    text = text.replace("\n","")   # remove linebreaks
    pieces = [text]
    for q in clif.CLIF_QUANTIFIERS:
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


def get_sentences(quantified_terms):
    """Reconstruct the sentences from a list of quantified terms in CLIF notation by matching parentheses.
    Returns a set of strings, each is a logical sentence surrounded by parentheses."""
    new_pieces = []
    pieces = quantified_terms
    #print pieces
    for i in range (0,len(pieces)):
        print pieces[i]
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
              

def get_variables(sentence):
    """Extract the variables from a logical sentence in CLIF notation."""
    variables = set([])
    pieces = [sentence[1:-1].strip()] # crop outer parentheses
    for q in clif.CLIF_QUANTIFIERS:
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
    
def get_nonlogical_symbols(sentence):
    """Extract all nonlogical symbols from a logical sentence in CLIF notation."""
    variables = get_variables(sentence)

    pieces = sentence.split()
    pieces = [p.split('(') for p in pieces]
    pieces = [item for sublist in pieces for item in sublist] # flatten list
    pieces = [p.split(')') for p in pieces]
    pieces = [item for sublist in pieces for item in sublist] # flatten list
    pieces = [p.strip() for p in pieces]
    print "removing variables " + str(variables) 
    pieces = set(pieces) - set(clif.CLIF_LOGICAL_CONNECTIVES) - set(clif.CLIF_OTHER_SYMBOLS) -set(['']) - set(variables)
    return pieces
     


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

