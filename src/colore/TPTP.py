'''
Created on 2012-11-28

@author: Torsten Hahmann
'''

import os, subprocess, time, shutil

class TPTP(object):

    # locations of the ladr_to_tptp translator (comes with Prover9-Mace4)
    # here it is simply assumed they are in the PATH
    LADR_TO_TPTP = 'ladr_to_tptp'

    TPTP_FOLDER = 'tptp'
    
    TPTP_ENDING = '.tptp'
    
    
    def ladr_to_tptp (self,input_file, output_file):    
    
        def get_tptp_basic_cmd ():
        
            tptp_command = TPTP.LADR_TO_TPTP + ' -q '
        
            return tptp_command
    
        
        def number_tptp_axioms (tptp_file):        
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
    
        cmd = get_tptp_basic_cmd()
        cmd += '< ' + input_file + ' > ' + output_file
        
        p = subprocess.Popen(cmd, shell=True, close_fds=True, preexec_fn=os.setsid)
        
        while p.returncode is None:
            time.sleep(2.0)
            p.poll()
        
        number_tptp_axioms(output_file)
        return p.returncode
    
