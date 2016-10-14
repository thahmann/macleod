import macleod.Filemgt as filemgt
import logging
import multiprocessing
from multiprocessing import Queue
import os
import re
import signal
import subprocess
import sys
import time


class ReasonerProcess(multiprocessing.Process):

    def __init__(self, args, output_filename, input_filenames, timeout, result_queue, log_queue):
        multiprocessing.Process.__init__(self)

        self.args = args
        self.result_queue = result_queue
        self.log_queue = log_queue
        self.exit = multiprocessing.Event()
        self.done = multiprocessing.Event()
        self.output_filename = output_filename
        self.input_filenames = input_filenames
        self.timeout = timeout	
        self.cputime = 0
        self.current_cputime = 0
        self.previous_cputime = 0

    def isDone (self):
        return self.done.is_set()

    def shutdown (self):
        record = filemgt.format(logging.LogRecord(self.__class__.__name__, logging.DEBUG, None, None, "RECEIVED ABORT SIGNAL: "  + self.name + ", command = " + self.args[0], None, None))
        self.log_queue.put(record)
        self.exit.set()

    def terminate (self):
        record = filemgt.format(logging.LogRecord(self.__class__.__name__, logging.INFO, None, None, "TERMINATING: " + self.name + ", command = " + self.args[0], None, None))
        self.log_queue.put(record)
        self.shutdown()
        time.sleep(0.2)
        multiprocessing.Process.terminate (self)

    def update_cputime (self, pid):
        new_cputime = get_cputime(pid)
        if new_cputime==0:
            return False
        #print "CPU time of " + self.args[0] + " = " + str(new_cputime)
        if new_cputime>=self.current_cputime:
            self.current_cputime = new_cputime
        else:
            #print "NEW PROCESS; previous_cputime = " + str(previous_cputime) 
            self.previous_cputime += self.current_cputime + 1
            self.current_cputime = new_cputime 			
        self.cputime = self.previous_cputime + self.current_cputime
        #print "total CPU time of " + self.args[0] + " = " + str(self.cputime)

    def enforce_limits (self, pid):
        limit = 1536 # each reasoning process is not allowed to use up more than 1.5GB of memory
        memory = get_memory(pid)
        #enforce memory limit
        if memory>limit:
            record = filemgt.format(logging.LogRecord(self.__class__.__name__, logging.INFO, None, None, "MEMORY EXCEEDED: " + self.name + ", command = " + self.args[0], None, None))
            self.log_queue.put(record)
            self.shutdown()
        # enforce time limit
        if self.cputime>self.timeout:
            record = filemgt.format(logging.LogRecord(self.__class__.__name__, logging.INFO, None, None, "TIME EXCEEDED: " + self.name + ", command = " + self.args[0], None, None))
            self.log_queue.put(record)
            self.shutdown()


    def run (self):
        record = filemgt.format(logging.LogRecord(self.__class__.__name__, logging.INFO, None, None, "STARTING: " + self.name + ", command = " + self.args[0], None, None))
        self.log_queue.put(record)
        out_file = open (self.output_filename, 'w')
        sp = startSubprocessWithOutput(self.args, out_file, self.input_filenames)				
        self.previous_cputime = 0
        self.current_cputime = 0
        while sp.poll() is None and not self.exit.is_set():
            time.sleep(1)
            self.update_cputime(sp.pid)
            self.enforce_limits(sp.pid)		
        if self.exit.is_set():
            # interrupted
            record = filemgt.format(logging.LogRecord(self.__class__.__name__, logging.DEBUG, None, None, "ABORTING: "  + self.name + ", command = " + self.args[0], None, None))
            self.log_queue.put(record)
#			print "RECEIVED ABORT SIGNAL"
            (_, stdoutdata) = terminateSubprocess(sp)
            if stdoutdata:
                stdoutdata = re.sub(r'[^\w]', ' ', stdoutdata)
                stdoutdata = ' '.join(stdoutdata.split())
                record = filemgt.format(logging.LogRecord(self.__class__.__name__, logging.INFO, None, None, "STDOUT from "  + self.name + ": " + str(stdoutdata), None, None))
                self.log_queue.put(record)
            self.result_queue.put((self.args[0], -1, stdoutdata))
            record = filemgt.format(logging.LogRecord(self.__class__.__name__, logging.INFO, None, None, "ABORTED: "  + self.name + ", command = " + self.args[0], None, None))
            self.log_queue.put(record)
            self.update_cputime(sp.pid)
            out_file.flush()
            out_file.close()
            self.writeHeader()
            self.done.set()
            return True
        # finished normally, i.e., sp.poll() determined the subprocess has terminated by itself
        self.update_cputime(sp.pid)
        self.result_queue.put((self.args[0], sp.returncode, None))
        record = filemgt.format(logging.LogRecord(self.__class__.__name__, logging.INFO, None, None, "FINISHED: "  + self.name + ", command = " + self.args[0], None, None))
        self.log_queue.put(record)
        out_file.flush()
        out_file.close()
        self.writeHeader()
        self.done.set()
        return True

    def writeHeader (self):
        import datetime
        """ Create a standardized footer for all output files that contains name of the program,
		the specific command, and a timestamp."""
        # list of input files
        time.sleep(0.2)
        cmd = self.args[0]
        for i in range(1,len(self.args)):
            cmd += " " + self.args[i]

        input_string = ""
        for in_file in self.input_filenames:
            input_string += " " + in_file

        #logging.getLogger(__name__).debug("WRITING STATISTICS to " + reasoner.getOutfile())				
        in_file =  open(self.output_filename, 'a')
        in_file.write('============================= ' + self.args[0] + ' ================================\n')
        #file.write(vampire.get_version()+'\n')
        now = datetime.datetime.now()
        in_file.write('execution finished: ' + now.strftime("%a %b %d %H:%M:%S %Y")+'\n')
        in_file.write("total CPU time used: " + str(self.cputime) +"\n")
        in_file.write('The command was \"' + cmd + '\"\n')
        in_file.write('Input read from ' + input_string + '\n')
        in_file.write('============================ end of footer ===========================\n')
        in_file.flush()
        in_file.close()


def get_cputime(pid):
    """Returns the CPU time a process has used so far in seconds as a float (one floating point digit)."""

    def cputime_win(pid):
        from wmi import WMI
        #print pid
        w = WMI('.')
        #	    result = w.query("SELECT * FROM Win32_PerfRawData_PerfProc_Process WHERE IDProcess=%d" % pid)
        result = w.query("SELECT * FROM Win32_Process WHERE ProcessId=%d" % pid)
        #print str(result)
        if not result:
            return 0
        else:
            return round((float(result[0].UserModeTime)) / 10000000, 1) # convert to seconds


    def cputime_nix(pid):
        # TODO: implement
        try:
            ps_process = subprocess.Popen("ps -g " + str(pid) + " -o time", shell=True, stdout=subprocess.PIPE)
            stdout_list = ps_process.communicate()[0].decode('utf-8').split('\n')
            while '' in stdout_list:
                stdout_list.remove('')
            stdout_list.pop(0)
            #print "CPU TIMES: " + str(stdout_list)
            seconds = 0
            for entry in stdout_list:
                time_chunks = entry.split(':')
                print(time_chunks)
                minute = time_chunks[0]
                second = time_chunks[1][0:1]
                print("Used time is %{0}m: %{1}".format(minute, second))
                seconds +=  int(minute)*60 + int(second) 
            return seconds
        except OSError as e:
            print(e)
            return 0


    cputime_default = cputime_nix

    handlers = {
            "nt": cputime_win, 
            "linux": cputime_nix
    }

    return handlers.get(os.name, cputime_default)(pid)



def get_memory(pid):

    def memory_win(pid):
        from wmi import WMI
        #print pid
        w = WMI('.')
        result = w.query("SELECT * FROM Win32_PerfRawData_PerfProc_Process WHERE IDProcess=%d" % pid)
        #print str(result)
        if not result:
            return 0
        else:
            return int(result[0].WorkingSet) // (1024*1024) # convert from Bytes to MB

    def memory_nix(pid):
        ps_process = subprocess.Popen("ps -g " + str(pid) + " -o rss", shell=True, stdout=subprocess.PIPE)
        stdout_list = ps_process.communicate()[0].decode('utf-8').split('\n')
        memory = 0
        while '' in stdout_list:
            stdout_list.remove('')
        stdout_list.pop(0)
        for entry in stdout_list:
            memory += int(entry)	
        return memory // 1024 # convert to MB

    memory_default = memory_nix

    handlers = {
            "nt": memory_win, 
            "linux": memory_nix
    }

    return handlers.get(os.name, memory_default)(pid)



def startSubprocessWithOutput(args, output_file, input_files=[]):
    """Start a new subprocess, but does not wait for the subprocess to complete. 
    This method uses the os.setsid in Linux, which is not available in Windows"""
    if os.name == 'nt':
        # Windows
        if len(input_files)==1:
            in_file = open(input_files[0],'r')
            p = subprocess.Popen(args, stdout=output_file, stderr=subprocess.STDOUT, stdin=in_file)
            in_file.close()
        else:
            p = subprocess.Popen(args, stdout=output_file, stderr=subprocess.STDOUT)
    else:
        # Linux (and others)
        if len(input_files)==1:
            in_file = open(input_files[0],'r')
            p = subprocess.Popen(args, preexec_fn=os.setsid, close_fds=True, stdout=output_file, stderr=subprocess.STDOUT, stdin=in_file)
            in_file.close()
        else:
            p = subprocess.Popen(args, preexec_fn=os.setsid, close_fds=True, stdout=output_file, stderr=subprocess.STDOUT)
    #print p.__class__
    return p


def startSubprocess(command):
    """Start a new subprocess, but does not wait for the subprocess to complete. 
    This method uses the os.setsid in Linux, which is not available in Windows"""
    if os.name == 'nt':
        # Windows
        p = subprocess.Popen(command, shell=True, close_fds=True)				
    else:
        # Linux (and others)
        logging.getLogger(__name__).debug("STARTING: " + command)
        p = subprocess.Popen(command, shell=True, preexec_fn=os.setsid, close_fds=True)

    #print p.__class__
    return p


def startInteractiveProcess(command):
    """Start a process whose output (STDOUT) is written to the return value."""
    if os.name == 'nt':
        # Windows
        p = subprocess.Popen(command, shell=True, close_fds=True, 
                                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    else:
        # Linux (and others)
        p = subprocess.Popen(command, shell=True, close_fds=True, preexec_fn=os.setsid, 
                                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return p



def executeSubprocess(command):
    """start a new subprocess and wait for it to terminate"""
    p = startSubprocess(command)
    p.wait()
    time.sleep(0.1)
    return p


def terminateSubprocess (process):
    """terminate a sub process."""
    def terminate_win (process):
        p = startSubprocessWithOutput("taskkill /F /T /PID " + str(process.pid), subprocess.PIPE)
        (stdout, _ ) = process.communicate()
        (stdout2, _ ) = p.communicate()
        #print "TYPE = " + stdout.__class__.__name__
        time.sleep(0.1)
        if not stdout:
            stdout = ""
        if not stdout2:
            stdout2 = ""
        re.sub(r'[^\w]', '', stdout)
        #stdoutdata = ' '.join(stdout.split())
        return (process.returncode, stdout+stdout2)  

    def terminate_nix (process):
        #os.killpg(process.pid, signal.SIGINT)
        return_value = None
        stdoutdata = ''
        try:
            return_value = process.terminate()
            time.sleep(0.1)
            stdoutdata = ""
            if process.poll() is None:
                return_value = os.kill(int(0-process.pid), signal.SIGINT)
                time.sleep(0.1)
            else:
                (stdout, _ ) = process.communicate()
                if stdout is not None:
                    re.sub(r'[^\w]', '', stdout)
                    stdoutdata = ' '.join(stdout.split())
        except OSError as e:
            print(e)
            pass 
        return (return_value, stdoutdata)

        #return os.waitpid(process.pid, os.WNOHANG)

    terminate_default = terminate_nix

    handlers = {
            "nt": terminate_win, 
            "linux": terminate_nix
    }

    return handlers.get(os.name, terminate_default)(process)


def raceProcesses (reasoners):
    """run a set of theorem provers and a set of model finders in parallel.
    If one terminates successfully, all others are immediately terminated.
    Parameters:
    reasoners -- list of Reasoners to execute.
    """
    from macleod.ClifModuleSet import ClifModuleSet

    results = Queue()

    processLogs = []

    reasonerProcesses = []

    # start all processes
    for r in reasoners:
        log = Queue()
        # TODO Figure out why r.timeout is a str in python3
        p = ReasonerProcess(r.getCommand(),r.getOutfile(), r.getInputFiles(), int(r.timeout), results, log)
        reasonerProcesses.append(p)
        processLogs.append(log)
        p.start()
        time.sleep(0.1)

    num_running = len(reasonerProcesses)
    success = False

    time.sleep(0.1)
    while num_running>0:	
        while results.empty():
            merged_log = merge(processLogs)
            if len(merged_log)>0:
                filemgt.add_to_subprocess_log(merged_log)
                #print "\n\n" + l + "\n\n"
            time.sleep(0.5)
            sys.stdout.write(".")
            #print "WAITING"
        # at least one process has terminated
        sys.stdout.write("\n")
        while not results.empty():
            num_running += - 1
            (name, code, _) = results.get()
            r = reasoners.getByCommand(name)
            r.setReturnCode(code)
            if r.terminatedSuccessfully():
                success = True
                if r.output==ClifModuleSet.INCONSISTENT:
                    if r.isProver():
                        logging.getLogger(__name__).info("FOUND PROOF: " + name)
                    else:
                        logging.getLogger(__name__).info("PROVED INCONSISTENCY: " + name)						
                elif r.output==ClifModuleSet.CONSISTENT:
                    if r.isProver():
                        logging.getLogger(__name__).info("FOUND COUNTEREXAMPLE: " + name)
                    else:
                        logging.getLogger(__name__).info("FOUND MODEL: " + name)
            else:
                logging.getLogger(__name__).info("TERMINATED WITHOUT SUCCESS: " + name)
                logging.getLogger(__name__).info("PROCESSES STILL RUNNING: " + str(num_running))

            # END OF PROCESSING QUEUE

        if success:
            for p in reasonerProcesses:
                logging.getLogger(__name__).debug("SENDING ABORT SIGNAL to " + p.args[0])				
                p.shutdown()
                while not p.isDone():
                    time.sleep(0.1)
            logging.getLogger(__name__).debug("Final processing of subprocess log queue")
            time.sleep(1)
            merged_log = merge(processLogs)
            filemgt.add_to_subprocess_log(merged_log)
            merged_log = []
            break

    # write statistics
#	time.sleep(1)
#	for r in reasonerProcesses:
#		r.writeHeader()

    return reasoners


def merge(logs):
    """ simple sort algorithm for merging the log queues from multiple processes"""

    merged_log = []

    # combine everything into a single list
    for i in range(0,len(logs)):
        while not logs[i].empty():
            merged_log.append(logs[i].get())
    return sorted(merged_log)
