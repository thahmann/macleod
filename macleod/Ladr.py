"""
POTATO
"""

import macleod.Filemgt as filemgt
import logging

def cumulate_ladr_files (input_files, output_file):    
    """write all axioms from a set of p9 files to a single file without any change in the content itself except for the replacement of certain symbols"""
    special_symbols = filemgt.get_tptp_symbols()

    logging.getLogger(__name__).debug('Special symbols: ' + str(special_symbols))

    text = []
    for f in input_files:
        in_file = open(f, 'r')
        line = in_file.readline()
        while line:
            if len(special_symbols)>0:
                for key in special_symbols:
                    line = line.replace(' '+key+'(', ' '+special_symbols[key]+'(')
                    line = line.replace('('+key+'(', '('+special_symbols[key]+'(')
            text.append(line)
            line = in_file.readline()
        in_file.close()

    text = strip_inner_commands(text)

    # store the location of all "<-" to be able to replace them back later on:

    out_file = open(output_file, 'w+')
    out_file.write('%axioms from module ' + f + ' and all its imports \n')
    out_file.write('%----------------------------------\n')
    out_file.write('\n')
    out_file.writelines(text) 
    out_file.close()
    return output_file



def strip_inner_commands(text):
    text = "".join(text)    # convert list of lines into a single string
    """remove all "formulas(sos)." and "end_of_list." from a p9 file assembled from multiple axiom files; leaving a single block of axioms"""
    parts = text.split("end_of_list.")
    # get the goal clauses
    goals = []
    for i in range(0,len(parts)):
        gparts = parts[i].split("formulas(goals).\n")
        if len(gparts)>2:
            # Problem!!
            raise LadrParsingError("Syntax error in ladr input: mismatch of 'formulas(goals).' and 'end_of_list.' keywords in" + ("".join(gparts)))
        elif len(gparts)==2:
            goals.extend([g.strip() + "\n" for g in gparts[1].split("\n")])
            parts[i] = parts[i].replace(parts[i],"").strip("\n").strip()
    # get the axioms
    axioms = []
    for i in range(0,len(parts)):
        aparts = parts[i].split("formulas(sos).\n")
        if len(aparts)>2:
            # Problem!!
            raise LadrParsingError("Syntax error in ladr input: mismatch of 'formulas(sos).' and 'end_of_list.' keywords in" + ("".join(aparts)))
        elif len(aparts)==2:
            axioms.extend([a.strip() + "\n" for a in aparts[1].split("\n")])
            parts[i] = parts[i].replace(parts[i],"").strip("\n").strip()

    # comment remainder
    for p in parts:
        text = ["% "+s.strip() +"\n" for s in p.split("\n")]

    # add axioms and goals
    if len(axioms)>0:
        text.append("formulas(sos).\n")
        text.extend(axioms)
        text.append("end_of_list.\n")
    if len(goals)>0: 
        text.append("formulas(goals).\n")
        text.extend(goals)
        text.append("end_of_list.\n")

    for p in text:
        if p == "%\n":
            text.remove(p)

    #print text
    return text


def get_ladr_goal_files (lemmas_file,  lemmas_name):
    """break a single lemma file into individual lemma files (with lemmas_name in its file name), each containing a single lemma."""
    sentences = split_lemma_into_sentences(lemmas_file)
    return get_lemma_files_from_sentences(lemmas_name, sentences)


def split_lemma_into_sentences(lemmas_file):
    """take a lemma file in the LADR format and split it into individual goals that can be feed into Prover9."""
    input_file = open(lemmas_file, 'r')
    lines = input_file.readlines()
    input_file.close()

    sentences = []

    started = False
    for line in lines:
        lineparts = line.strip().split('%')
        #print lineparts
        if lineparts[0]:
            lineparts[0] = lineparts[0].strip('\n').strip()
            if len(lineparts[0])>0:
                if not started:
                    if line.find('formulas(sos).') > -1 or line.find('formulas(assumptions).') > -1:
                        started  = True
                else:
                    if line.find('end_of_list.') > -1:
                        break
                    else:
                        sentences.append(lineparts[0])

    logging.getLogger(__name__).info('Split ' + lemmas_file + ' into ' + str(len(sentences)) + ' individual lemma files')
    return sentences



def get_lemma_files_from_sentences (lemmas_name, sentences):

    sentences_files = []
    sentences_names = []

    import math
    # determine maximal number of digits
    digits = int(math.ceil(math.log10(len(sentences))))

    i = 1

    for lemma in sentences:
        name = lemmas_name + '_goal' + ('{0:0'+ str(digits) +  'd}').format(i)

        filename = filemgt.get_full_path(name, 
                              folder=filemgt.read_config('ladr','folder'), 
                              ending=filemgt.read_config('ladr','ending'))        
        output_file = open(filename, 'w')
        output_file.write('formulas(goals).\n')
        output_file.write(lemma + '\n')
        output_file.write('end_of_list.\n')
        output_file.close()
        sentences_files.append(filename)
        sentences_names.append(name)
        i += 1

    return (sentences_names, sentences_files)


class LadrParsingError(Exception):

    output = []

    def __init__(self, value, output=[]):
        self.value = value
        self.output = output
        logging.getLogger(__name__).error(repr(self.value) + '\n\n' + (''.join('{}: {}'.format(*k) for k in enumerate(self.output))))
    def __str__(self):
        return repr(self.value) + '\n\n' + (''.join('{}: {}'.format(*k) for k in enumerate(self.output)))


