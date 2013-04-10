import os, signal, time, subprocess, logging, re, sys
import process, filemgt
import multiprocessing
from multiprocessing import Queue
from multiprocessing import Event

class ReasonerProcess(multiprocessing.Process):
	
	def __init__(self, args, output_filename, input_filenames, result_queue, log_queue):
		multiprocessing.Process.__init__(self)

		self.args = args
		self.result_queue = result_queue
		self.log_queue = log_queue
		self.exit = multiprocessing.Event()
		self.done = multiprocessing.Event()
		self.output_filename = output_filename
		self.input_filenames = input_filenames
		
		#print str(args) + " > " + self.output_filename

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
				
	def run (self):
		record = filemgt.format(logging.LogRecord(self.__class__.__name__, logging.INFO, None, None, "STARTING: " + self.name + ", command = " + self.args[0], None, None))
		self.log_queue.put(record)
		file = open (self.output_filename, 'w')
		sp = process.startSubprocessWithOutput(self.args, file, self.input_filenames)				
		self.cputime = 0	# total cputime
		previous_cputime = 0
		current_cputime = 0
		while sp.poll() is None and not self.exit.is_set():		
			#logging.getLogger(__name__).info("WAITING: " + self.command)
			new_cputime = get_cputime(sp.pid)
			if new_cputime>=current_cputime:
				current_cputime = new_cputime
			else:
				print "NEW PROCESS; previous_cputime = " + str(previous_cputime) 
				previous_cputime += current_cputime + 1
				current_cputime = new_cputime 			
			self.cputime = previous_cputime + current_cputime
			#print self.cputime
			time.sleep(1)
			limit = 1536 # each reasoning process is not allowed to use up more than 1.5GB of memory
			memory = get_memory(sp.pid)
			#print memory
			if memory>limit:
				record = filemgt.format(logging.LogRecord(self.__class__.__name__, logging.INFO, None, None, "MEMORY EXCEEDED: " + self.name + ", command = " + self.args[0], None, None))
				self.log_queue.put(record)
				self.shutdown()
		if self.exit.is_set():
			# interrupted
			record = filemgt.format(logging.LogRecord(self.__class__.__name__, logging.DEBUG, None, None, "ABORTING: "  + self.name + ", command = " + self.args[0], None, None))
			self.log_queue.put(record)
#			print "RECEIVED ABORT SIGNAL"
			new_cputime = get_cputime(sp.pid)
			if new_cputime >=current_cputime:
				current_cputime = new_cputime
			else:
				previous_cputime += current_cputime + 1
				current_cputime = new_cputime	
			self.cputime = previous_cputime + current_cputime
			(p, stdoutdata) = process.terminateSubprocess(sp)
			if stdoutdata:
				stdoutdata = re.sub(r'[^\w]', ' ', stdoutdata)
				stdoutdata = ' '.join(stdoutdata.split())
				record = filemgt.format(logging.LogRecord(self.__class__.__name__, logging.INFO, None, None, "STDOUT from "  + self.name + ": " + str(stdoutdata), None, None))
				self.log_queue.put(record)
#			(stdoutdata, _) = sp.communicate()
#			if stdoutdata:
#				print stdoutdata.__class__.__name__
#				stdoutdata = re.sub(r'[^\w]', ' ', stdoutdata)
#				stdoutdata = ' '.join(stdoutdata.split())
#				record = filemgt.format(logging.LogRecord(self.__class__.__name__, logging.INFO, None, None, "STDOUT from "  + self.name + ": " + str(stdoutdata), None, None))
#				self.log_queue.put(record)
			# default return code for aborted process: -1
			self.result_queue.put((self.args[0], -1, stdoutdata))
			record = filemgt.format(logging.LogRecord(self.__class__.__name__, logging.INFO, None, None, "ABORTED: "  + self.name + ", command = " + self.args[0], None, None))
			self.log_queue.put(record)
			#print "+++ HERE +++"
			# for the record, write the CPU time to the end of the file
			file.write("TOTAL CPU TIME USAGE = " + str(self.cputime))
			file.close()
			self.done.set()
			return True
		# finished normally, i.e., sp.poll() determined the subprocess has terminated by itself
		self.result_queue.put((self.args[0], sp.returncode, None))
		record = filemgt.format(logging.LogRecord(self.__class__.__name__, logging.INFO, None, None, "FINISHED: "  + self.name + ", command = " + self.args[0], None, None))
		self.log_queue.put(record)
		# for the record, write the CPU time to the end of the file
		self.cputime = max(self.cputime, get_cputime(sp.pid))
		file.write("TOTAL CPU TIME USAGE = " + str(self.cputime) +"\n")
		file.close()
		self.done.set()
		return True
	

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
			stdout_list = ps_process.communicate()[0].split('\n')
			while '' in stdout_list:
				stdout_list.remove('')
			stdout_list.pop(0)
			#print "CPU TIMES: " + str(stdout_list)
			seconds = 0
			for entry in stdout_list:
				time_chunks = entry.split(":")
				seconds += int(time_chunks[0])*3600 + int(time_chunks[1])*60 + int(time_chunks[2]) 
			return seconds
		except OSError as e:
			print e
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
		stdout_list = ps_process.communicate()[0].split('\n')
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
			file = open(input_files[0],'r')
			p = subprocess.Popen(args, stdout=output_file, stderr=subprocess.STDOUT, stdin=file)
			file.close()
		else:
			p = subprocess.Popen(args, stdout=output_file, stderr=subprocess.STDOUT)
	else:
		# Linux (and others)
		if len(input_files)==1:
			file = open(input_files[0],'r')
			p = subprocess.Popen(args, preexec_fn=os.setsid, close_fds=True, stdout=output_file, stderr=subprocess.STDOUT, stdin=file)
			file.close()
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
		logging.getLogger(__name__).info("STARTING: " + command)
		p = subprocess.Popen(command, shell=True, preexec_fn=os.setsid, close_fds=True)
	
	#print p.__class__
	return p


def startInteractiveProcess():
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
	p = process.startSubprocess(command)
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
		stdoutdata = ' '.join(stdout.split())
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
			print e
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
	
	Keyword arguments:
	provers -- dictionary of theorem provers to execute where the key is the command and the value a set of return codes that indicate success.
	modelfinders -- dictionary of modelfinders to execute where the key is the command and the value a set of return codes that indicate success.
	"""
	from src import ClifModuleSet
	#time.sleep(0.1)
	
	results = Queue()

	processLogs = []
	
	reasonerProcesses = []
	
	# start all processes
	for r in reasoners:
		log = Queue()
		p = ReasonerProcess(r.getCommand(),r.getOutfile(), r.getInputFiles(), results, log)
		reasonerProcesses.append(p)
		processLogs.append(log)
		#p = multiprocessing.Process(name=r.identifier, target=executeSubprocess, args=(r.getCommand(),results,))
		p.start()
		time.sleep(0.1)
		#i += 1

	num_running = len(reasonerProcesses)
	success = False
	
	time.sleep(0.1)
	#active=multiprocessing.active_children()
	while num_running>0:	
		while results.empty():
			merged_log = merge(processLogs)
			if len(merged_log)>0:
				filemgt.add_to_subprocess_log(merged_log)
				#print "\n\n" + l + "\n\n"
			time.sleep(0.5)
			sys.stdout.write(".")
			#print "WAITING"
			#active=multiprocessing.active_children()	# poll for active processes
		# at least one process has terminated
		sys.stdout.write("\n")
		while not results.empty():
			num_running += - 1
			(name, code, _) = results.get()
			r = reasoners.getByCommand(name)
			r.setReturnCode(code)
			#if not r.name.lower()=="paradox":	# TODO: fix permanently: Paradox returns code 0 even though it did not find a model
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
#			else: # for paradox
#				logging.getLogger(__name__).info("TERMINATED (SUCCESS UNKNOW): " + name)
#				logging.getLogger(__name__).info("PROCESSES STILL RUNNING: " + str(num_running))
				
			# END OF PROCESSING QUEUE
			
		if success:
			for p in reasonerProcesses:
				logging.getLogger(__name__).debug("SENDING ABORT SIGNAL to " + p.args[0])				
				p.shutdown()
				while not p.isDone():
					time.sleep(0.1)
			logging.getLogger(__name__).debug("Final processing of subprocess log queue")
			time.sleep(0.5)
			merged_log = merge(processLogs)
			filemgt.add_to_subprocess_log(merged_log)
			merged_log = []
			break

	return reasoners


def merge(logs):
	""" simple sort algorithm for merging the log queues from multiple processes"""

	merged_log = []

	# combine everything into a single list
	for i in range(0,len(logs)):
		while not logs[i].empty():
			merged_log.append(logs[i].get())
	return sorted(merged_log)
