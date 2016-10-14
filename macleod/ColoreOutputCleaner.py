'''
Created on 2012-11-28

@author: Torsten Hahmann
'''

import os, os.path
import sys
import calendar
import locale
from .ClifModule import ClifModule
from ColoreFileManager import ColoreFileManager
from .ProofStatistic import ProofStatistic
from .LADR import LADR
from TPTP import TPTP
from .VAMPIRE import VAMPIRE 
from datetime import datetime

class ColoreOutputCleaner(object):

    # keep track of all the process files
    processed = []

    # where to document the work
    stat_filename = ''
    statFile = None

    directory = "."
    # list of abbreviated months
    months = dict([(calendar.month_abbr[index],index) for index in range(1,len(calendar.month_abbr))])

    def __init__(self, filename, directory=None):
        try:
            locale.setlocale(locale.LC_ALL, 'en_US')
            locale.setlocale(locale.LC_ALL, 'enu')
        except locale.Error as e:
            #print locale.getdefaultlocale()
            #print e
            pass
        if len(directory)>0:
            self.directory = directory
        self.stat_filename = filename

    def setDirectory(directory):
        self.directory = directory

    # delete unnecessary files

    def cleanAll(self):
        # append to statsfile; otherwise overwrites old stats
        self.statFile = open(self.stat_filename,'a')
        self.statFile.writelines(['----------------------------\n','Cleaning up outputs\n'
                                                        ,str(datetime.utcnow())+' UTC\n'
                                                        ,'----------------------------\n'])
        processed = []
        for root, dirs, files in os.walk(self.directory):
            for f in files:
                fullpath = os.path.join(root, f)
                # delete options single_file
                if fullpath.endswith(LADR.P9_OPTIONS_FILE_NAME):
                    self.removeFile(fullpath)
                # delete intermediary files
                if fullpath.endswith('.p9i') or fullpath.endswith('.p9' + ClifModule.CLIF_ENDING):
                    self.removeFile(fullpath)
                if fullpath.endswith('.out'):
                    if not self.getShortFileName(fullpath) in self.processed:
                        self.statFile.write('\n')
                        self.cleanProofs(fullpath,self.statFile)
                        self.processed.append(self.getShortFileName(fullpath))
                    #print 'add ' + fullpath.rsplit('.',2)[0] + ' to processed'
        self.statFile.close()
        return self.stat_filename


    def getShortFileName(self,single_file):
        # remove possible extra '.relevance' ending for Paradox and Vampire outputs
        first_filename = self.getLongFileName(single_file)
        if len(first_filename.split('.'))>1:
            first_filename = first_filename.split('.')[0]
        return first_filename

    def getLongFileName(self,single_file):
        filename = os.path.basename(single_file)
        # remove ".out" ending
        filename = filename[:filename.rfind('.')]
        # remove identifying ending (".m4",".p9",".vam", or ".tptp")
        filename = filename[:filename.rfind('.')]
        return filename


    # remove outputs that are unneccessary
    def cleanProofs(self,single_file,statfile):
        filename = self.getLongFileName(single_file)
        first_filename = self.getShortFileName(single_file)
        print(first_filename)

        #print os.path.normcase(os.path.join(os.path.dirname(single_file),filename+'.m4.out'))
        filename_mace4 = os.path.normcase(os.path.join(os.path.dirname(single_file),filename+ LADR.MACE4_ENDING + '.out'))
        filename_prover9 = os.path.normcase(os.path.join(os.path.dirname(single_file),filename+ LADR.PROVER9_ENDING + '.out'))
        filename_paradox3 = os.path.normcase(os.path.join(os.path.dirname(single_file),first_filename+ TPTP.TPTP_ENDING + '.out'))
        filename_vampire = os.path.normcase(os.path.join(os.path.dirname(single_file),first_filename+ VAMPIRE.VAMPIRE_ENDING + '.out'))

        proof = False
        model = False
        mace4_stats = None
        prover9_stats = None
        paradox3_stats = None
        vampire_stats = None
        self.statFile.write(os.path.normcase(os.path.join(os.path.dirname(single_file),first_filename)) + ' tested with: ')
        before = False
        if os.path.isfile(filename_mace4):
            if before:
                self.statFile.write(', ')
            before = True
            self.statFile.write(ProofStatistic.MACE4)
            mace4_stats = self.getMace4Stats(filename_mace4)
            if mace4_stats.success:
                model = True
        if os.path.isfile(filename_prover9):
            if before:
                self.statFile.write(', ')
            before = True
            self.statFile.write(ProofStatistic.PROVER9)
            prover9_stats = self.getProver9Stats(filename_prover9)
            if prover9_stats.success:
                proof = True
        if os.path.isfile(filename_paradox3):
            if before:
                self.statFile.write(', ')
            before = True
            self.statFile.write(ProofStatistic.PARADOX3)
            paradox3_stats = self.getParadox3Stats(filename_paradox3)
            if paradox3_stats.success:
                model = True
        if os.path.isfile(filename_vampire):
            if before:
                self.statFile.write(', ')
            before = True
            self.statFile.write(ProofStatistic.VAMPIRE)
            vampire_stats = self.getVampireStats(filename_vampire)
            if vampire_stats.success:
                proof = True

        self.statFile.write('\n')

        # detect conflicts and unknown results: a model and a proof were found
        # write output (stats single_file)
        conflict = False
        unknown = False
        if (model and proof):
            conflict = True
            self.statFile.write('CONFLICT: ' + os.path.normcase(os.path.join(os.path.dirname(single_file),first_filename)) +'\n')
        elif (not model and not proof):
            unknown = True
            self.statFile.write('UNKNOWN: ' + os.path.normcase(os.path.join(os.path.dirname(single_file),first_filename)) +'\n')

        if prover9_stats:
            if prover9_stats.success:
                self.statFile.write('SUCCESS: ' + filename_prover9
                                                        + ' IN ' + prover9_stats.elapsed
                                                        + ' ON ' + prover9_stats.date + ' ' + prover9_stats.time
                                                        + ', PROOF LENGTH=' + prover9_stats.size +'\n')				
            else:
                self.statFile.write('\t FAILED: ' + filename_prover9
                                                        + ' IN ' + prover9_stats.elapsed
                                                        + ' ON ' + prover9_stats.date + ' ' + prover9_stats.time +'\n')				
                self.removeFile(filename_prover9)
        if vampire_stats:
            if vampire_stats.success:
                self.statFile.write('SUCCESS: ' + filename_vampire
                                                        + ' IN ' + vampire_stats.elapsed +'\n')			
            else:
                self.statFile.write('\t FAILED: ' + filename_vampire
                                                        + ' IN ' + vampire_stats.elapsed +'\n')			
                self.removeFile(filename_vampire)
        if mace4_stats:
            if mace4_stats.success:
                self.statFile.write('SUCCESS: ' + filename_mace4
                                                        + ' IN ' + mace4_stats.elapsed
                                                        + ' ON ' + mace4_stats.date + ' ' + mace4_stats.time
                                                        + ', MODEL SIZE=' + mace4_stats.size +'\n')				
            else:
                self.statFile.write('\t FAILED: ' + filename_mace4
                                                        + ' IN ' + mace4_stats.elapsed
                                                        + ' ON ' + mace4_stats.date + ' ' + mace4_stats.time +'\n')				
                if os.path.isfile(filename_mace4):
                    self.removeFile(filename_mace4)
        if paradox3_stats:
            if paradox3_stats.success:
                self.statFile.write('SUCCESS: ' + filename_paradox3
                                                        + ', MODEL SIZE=' + str(paradox3_stats.size) +'\n')			
            else:
                self.statFile.write('\t FAILED: ' + filename_paradox3 
                                                        + ', ATTEMPTED UP TO MODEL SIZE=' + str(paradox3_stats.size) +'\n')			
                if os.path.isfile(filename_paradox3):
                    self.removeFile(filename_paradox3)

        self.statFile.write('\n')
        return first_filename



    def getVampireStats(self, filename):
        single_file = open(filename)
        # create new ProofStatistic
        stats = ProofStatistic(ProofStatistic.VAMPIRE)
        stats.filename = os.path.basename(filename)
        line = single_file.readline()
        total_time = 0.0
        while line:
            # check if a proof was found
            if not stats.success and 'SZS output start Proof' in line:
                stats.success = True
                print('Vampire successful')
            if line.startswith('Time elapsed'):
                #print line
                total_time += float(line.split()[2].strip())
            line = single_file.readline()
        print(total_time)
        stats.elapsed = str(total_time)
        single_file.close()
        return stats


    def getParadox3Stats(self, filename):
        single_file = open(filename)
        # create new ProofStatistic
        stats = ProofStatistic(ProofStatistic.PARADOX3)
        stats.filename = os.path.basename(filename)
        line = single_file.readline()
        stats.size = -1
        while line:
            # check if a proof was found
            if line.startswith('+++ RESULT:'):
                if 'Satisfiable' in line:
                    stats.success = True
            if 'domain size is' in line:
                # extract the model size
                size = int(line.split('domain size is')[1].strip())
                if stats.size< size:
                    stats.size = size
                #print 'extracting domain size=' + stats.size
            elif 'domain size' in line:
                # extract the size of to which models where checked
                size = int(line.split('domain size')[1].strip())
                if stats.size< size:
                    stats.size = size-1
            line = single_file.readline()
        single_file.close()
        return stats


    def getProver9Stats(self, filename):
        single_file = open(filename)
        # create new ProofStatistic
        stats = ProofStatistic(ProofStatistic.PROVER9)
        stats.filename = os.path.basename(filename)
        line = single_file.readline()
        while line:
            # check if a proof was found
            if line.startswith('THEOREM PROVED'):
                stats.success = True
            # extract length of proof
            if line.startswith('% Length of proof is'):
                line = line.rstrip().replace('% Length of proof is','')
                # extract the proof length
                stats.size = line.split('.')[0].strip()
            # get process CPU time
            self.extractProver9Mace4CPUTime(line,stats)
            # get process date
            self.extractProver9Mace4Date(line,stats)
            line = single_file.readline()
        single_file.close()
        return stats



    def getMace4Stats(self,filename):
        single_file = open(filename)
        # create new ProofStatistic
        stats = ProofStatistic(ProofStatistic.MACE4)
        stats.filename = os.path.basename(filename)
        line = single_file.readline()
        while line:
            # check if a model was found
            if line.startswith('interpretation( '):
                stats.success = True
                line = line.rstrip().replace('interpretation( ','')
                # extract the domain size of the model
                stats.size = line.split(',')[0]
            # get process CPU time
            self.extractProver9Mace4CPUTime(line,stats)
            # get process date
            self.extractProver9Mace4Date(line,stats)
            line = single_file.readline()
        single_file.close()
        return stats


    def extractProver9Mace4CPUTime(self, line,stats):
        if line.startswith('User_CPU='):
            line = line.replace('User_CPU=','')
            # extract the time needed
            stats.elapsed = line.rstrip().split(',')[0]
            return


    def extractProver9Mace4Date(self,line,stats):
        if line.startswith('Process'):
            if 'exit' in line:
                exit_line = line.rstrip().split()
                #print exit_line
                # convert abbreviated month to number
                month = str(self.months[exit_line[5]])				
                day = exit_line[6]				
                stats.time = exit_line[7]				
                year = exit_line[8]				
                stats.date = year + '-' + month + '-' + day
                return

    # delete a single_file and record the deletion in the stats (log) single_file
    def removeFile(self, filename):
        self.statFile.write('\t\t DELETED: ' + filename +'\n')			
        os.remove(filename)

    @staticmethod
    def print_help():
        print('Ontology tool suite for ontology verification in COLORE:')
        print('Copyright 2010-2012: Torsten Hahmann')
        print('----------')
        print('----------')
        print('')
        print('USAGE 1: ColoreOutputCleaner outputfile directory')
        print('----------')


# run program

if __name__ == '__main__':

    options = sys.argv
    if not options or len(options)<2 or len(options)>3:
        ColoreOutputCleaner.print_help()
        sys.exit()
    elif '-h' in options:
        options.remove('-h')
        ColoreOutputCleaner.print_help()
        sys.exit()
    elif len(options)==2:
        print(options[0])
        print('Output single_file: ' + options[1])
        coc = ColoreOutputCleaner(options[1])
        coc.cleanAll()
    elif len(options)==3:
        print(options[0])
        print('Output single_file: ' + options[1])
        print('Directory to process: ' + options[2])
        coc = ColoreOutputCleaner(options[1],options[2])
        coc.cleanAll()
