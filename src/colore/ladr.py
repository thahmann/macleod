import ladr

def cumulate_ladr_files (input_files, output_file, special_symbols):    
    """write all axioms from a set of p9 files to a single file without any change in the content itself except for the replacement of certain symbols"""
    text = []
    for f in input_files:
        in_file = open(f, 'r')
        line = in_file.readline()
        while line:
            if special_symbols:
                for (key, replacement) in special_symbols:
                    line = line.replace(' '+key+'(', ' '+replacement+'(')
                    line = line.replace('('+key+'(', '('+replacement+'(')
            text.append(line)
            line = in_file.readline()
        in_file.close()
    
    text = strip_inner_commands(text)
    text = comment_imports(text)
    file = open(output_file, 'w+')
    file.write('%axioms from module ' + f + ' and all its imports \n')
    file.write('%----------------------------------\n')
    file.write('\n')
    file.writelines(text) 
    file.close()
    return output_file
    
def strip_inner_commands(text):
    text = ''.join(text)    # convert list of lines into a single string
    """remove all "formulas(sos)." and "end_of_list." from a p9 file assembled from multiple axiom files; leaving a single block of axioms"""
    parts = text.split('formulas(sos).\n',1)
    text = parts[0] +'formulas(sos).\n' + parts[1].replace('formulas(sos).\n','')
    i = text.count('end_of_list.\n')
    text = text.replace('end_of_list.\n','',i-1)
    return [(t + '\n') for t in text.split('\n')]   # convert back into a list of lines


def comment_imports (text):
    print "Commenting imports in LADR file"
    for i in range(0,len(text)):
        keyword = 'imports('    # this is the syntax used by the clif-to-prover9 converter
        if text[i].strip().find(keyword) > -1:
            print 'module import found: ' + text[i]
            text[i] = '% ' + text[i]
            #new_module_name = line.strip()[len(keyword)+1:-3].strip()
        else:
            pass
    return text
        


