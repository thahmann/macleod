import os, ladr, filemgt

replaced = False

def cumulate_ladr_files (input_files, output_file):    
    """write all axioms from a set of p9 files to a single file without any change in the content itself except for the replacement of certain symbols"""
    special_symbols = filemgt.get_tptp_symbols()
    
    print str(special_symbols)
    
    filemgt.read_config('converters','clif-to-prover9')
    
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
    text = comment_imports(text)
    
    # store the location of all "<-" to be able to replace them back later on:
   
    file = open(output_file, 'w+')
    file.write('%axioms from module ' + f + ' and all its imports \n')
    file.write('%----------------------------------\n')
    file.write('\n')
    file.writelines(text) 
    file.close()
    return output_file

def number_tptp_axioms (tptp_file):
    """Give each axiom in a TPTP file a unique number and convert CNF lines to FOF lines."""       
    f = open(tptp_file, 'r')
    lines = f.readlines()
    f.close()
    f = open(tptp_file, 'w')
    counter = 1
    for line in lines:
        line = line.replace('cnf(sos,','cnf(sos'+str(counter)+',')
        line = line.replace('fof(sos,','fof(sos'+str(counter)+',')
        f.write(line)
        counter += 1
    f.close()
    return


def replace_equivalences(ladr_file):
    if os.name == 'nt': 
        file = open(ladr_file, 'r')
        text = file.readlines()
        file.close()   
        
            # ensure proper spacing
        text = [s.replace("<->"," <iff> ") for s in text]
        ladr.replaced = False
    
        if " <iff> " in "".join(text):
            print "replacing equivalences"
            if "<-" in "".join(text):
                print "Problem converting LADR files to TPTP syntax: cannot deal with <-> properly in Windows due to error in 2007 version of old ladr_to_tptp."
                return
            else:
                text = [s.replace("<iff>","<-") for s in text]
                ladr.replaced = True
    
        file = open(ladr_file, 'w+')
        file.writelines(text) 
        file.close()
        return ladr_file
    


def replace_equivalences_back(tptp_file):
    """ correct equivalences in the TPTP output"""
    if not os.name == 'nt' or not ladr.replaced:
        return
    ladr.replaced = False
    file = open(tptp_file, 'r')
    text = file.readlines()
    file.close()   
    file = open(tptp_file, 'w+')
    file.writelines([s.replace("<=","<=>") for s in text]) 
    file.close()
    return tptp_file
    
    
def strip_inner_commands(text):
    text = ''.join(text)    # convert list of lines into a single string
    """remove all "formulas(sos)." and "end_of_list." from a p9 file assembled from multiple axiom files; leaving a single block of axioms"""
    parts = text.split('formulas(sos).\n',1)
    text = parts[0] +'formulas(sos).\n' + parts[1].replace('formulas(sos).\n','')
    i = text.count('end_of_list.\n')
    text = text.replace('end_of_list.\n','',i-1)
    return [(t + '\n') for t in text.split('\n')]   # convert back into a list of lines


def comment_imports (text):
    #print "Commenting imports in LADR file"
    for i in range(0,len(text)):
        keyword = 'imports('    # this is the syntax used by the clif-to-prover9 converter
        if text[i].strip().find(keyword) > -1:
            #print 'module import found: ' + text[i]
            text[i] = '% ' + text[i]
            #new_module_name = line.strip()[len(keyword)+1:-3].strip()
        else:
            pass
    return text
        


