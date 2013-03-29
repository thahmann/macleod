'''
Created on 2010-11-26
New module created on 2013-03-16

@author: Torsten Hahmann
'''
import os, logging, clif

# logical connectives in CLIF
CLIF_LOGICAL_CONNECTIVES = ['not', 'and', 'or', 'iff', 'if', 'exists', 'forall', '=']
# CLIF symbols that are logically irrelevant
CLIF_OTHER_SYMBOLS = ['cl-text', 'cl-module', 'cl-imports']
# CLIF quantifiers
CLIF_QUANTIFIERS = ['forall', 'exists']

CLIF_IMPORT = 'cl-imports'

CLIF_COMMENT = 'cl-comment'


def remove_all_comments(input_file, output_file):
    """Remove all comments (multi-line and single-line comments), including cl-comment blocks from the given file"""

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
            


# get the named entities (functions and relations) from a string
def get_logical_symbols_from_single_line(line):
    #print 'line: ' + line 
    
    symbols = set([])
    
    s = line.find('(')
    while  s > -1:
        #print 'line before: ' + line
        line = line[s+1:]
        #print 'reduced line: ' + xline

        # we need the first closing parenthesis 
        e = line.find(')')
        
        if e<0:
            # no closing parenthesis
            activepart = line
            line = ''
        else:
            # find last  open parenthesis before the closing one
            s2 = line.rfind('(', 0, e)
            if s2<0:
                # no other parenthesis
                # split the line into an active parts that is immediately processed and the remainder of the line
                activepart = line[0:e]
                line = line[e+1:]
            else:
                activepart = line[s2+1:e]
                line = line[0:s2] + ' ' + line[e+1:]
                
        #print 'active part: ' + activepart
        
        if len(activepart)!=0:
        #print 'remainder of line: ' + line
        # split the active part into words
            words = activepart.split()
            
            if words[0] in clif.CLIF_LOGICAL_CONNECTIVES:
                # remove the connective, add the remainder to the remaining line
                line = activepart[len(words[0]):] + line
                #print 'line after processing connectives: ' + line
            elif words[0] not in clif.CLIF_OTHER_SYMBOLS:
                symbols.add(words[0])
        # next one 
        s = line.find('(')
    
    return symbols


def get_quantified_variables_from_single_line (line):
    #print 'line (initial) = ' + line
    line = line.strip()
    #print 'all variables: ' + str(logical_vars)

    vars = set([])
    
    for keyword in clif.CLIF_QUANTIFIERS:
        
        i = line.find(keyword+ " ")
        while  i > -1:
            #print 'line: ' + line
            s = line.find('(',i)
            e = line.find(')', s)
            var_string = line[s+1:e]
            #print var_string
            remainder = line[e:]
            #print 'logical_vars: ' + var_string
            #print 'remainder: ' + remainder                   
            for var in var_string.split():
                vars.add(var)
            line = remainder
            i = line.find(keyword)
    return vars

        
def get_imports(input_file):
    """Find all the imported modules"""

    imports = set([])
    
    cl_file = open(input_file, 'r')
    line = cl_file.readline()
    while line:           
        c1 = line.find(clif.CLIF_IMPORT)
        if c1>-1:
            
            imports.add(line[c1:].split(' ',1)[1].split(')')[0].strip())
        line = cl_file.readline()
    cl_file.close()
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

