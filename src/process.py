import os, signal, time, subprocess, logging
import process
from multiprocessing import Queue

def startSubprocess(command):
	"""Start a new subprocess, but does not wait for the subprocess to complete. 
	This method uses the os.setsid in Linux, which is not available in Windows"""
	logging.getLogger(__name__).info("STARTING: " + command)
	if os.name == 'nt':
		# Windows
		p = subprocess.Popen(command, shell=True, close_fds=True)
	else:
		# Linux (and others)
		p = subprocess.Popen(command, shell=True, close_fds=True, preexec_fn=os.setsid)
	
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
	
			



def executeSubprocess(command, results = None):
	"""start a new subprocess and wait for it to terminate"""
	p = process.startSubprocess(command)
	p.wait()
	#print str(p.returncode) + '\n'
	if p.returncode==0:
		# give a bit of time to finish the command line output
		time.sleep(0.1)
		logging.getLogger(__name__).info("FINISHED: " + command)
		if results:
			results.put((command, p.returncode))
			return
		else:
			return p

		

def terminateSubprocess (process):
	"""terminate a sub process; needed for downwards compatibility with Python 2.5"""
	def terminate_win (process):
		logging.getLogger(__name__).debug("Terminating Windows process " + str(process.pid))
		value = os.system("taskkill /F /T /PID " + str(process.pid))
		#value = win32process.TerminateProcess(process._handle, -1)
#		import win32api
#		PROCESS_TERMINATE = 1
#		handle = win32api.OpenProcess(PROCESS_TERMINATE, False, process.pid)
#		win32api.TerminateProcess(handle, -1)
#		win32api.CloseHandle(handle)
		time.sleep(0.5)
		return value

	def terminate_nix (process):
		logging.getLogger(__name__).debug("Terminating Linux process " + str(process.pid))
		#os.kill(process.pid, signal.SIGINT)
		process.terminate()
		if process.is_alive():
			value = os.kill(process.pid, signal.SIGINT)
			time.sleep(0.5)
			return value

		#return os.waitpid(process.pid, os.WNOHANG)

	terminate_default = terminate_nix
	
	handlers = {
		"nt": terminate_win, 
		"linux": terminate_nix
	}

	return handlers.get(os.name, terminate_default)(process)

#def run(command):
#	print command + ' is active'
#		process.startSubprocess(prover)
#		process.wait()
#		print command + ' returned with code ' + process.returncode
#		return process.returncode


def raceProcesses (reasoners):
	"""run a set of theorem provers and a set of model finders in parallel.
	If one terminates successfully, all others are immediately terminated.
	
	Keyword arguments:
	provers -- dictionary of theorem provers to execute where the key is the command and the value a set of return codes that indicate success.
	modelfinders -- dictionary of modelfinders to execute where the key is the command and the value a set of return codes that indicate success.
	"""
	time.sleep(0.1)
	
	#print provers
	#print modelfinders
	
	reasonerProcesses = []
	
	# dictionary that give each process a number as name to not have to rely on the command that is altered through serialization
	#proverDict = {}
	#i = 1
	
	import multiprocessing
	
	results = Queue()
	
	# start all processess
	for r in reasoners:
		#print 'Creating subprocess for ' + r
		#proverDict[i] = r
		# TODO: need a separate class for the execute method in order to gracefully shut it down
		p = multiprocessing.Process(name=r.identifier, target=executeSubprocess, args=(r.getCommand(),results,))
		p.start()
		time.sleep(0.1)
		reasonerProcesses.append(p)
		#i += 1
	
	num_running = len(reasonerProcesses)
	success = False
	
	time.sleep(0.1)
	#active=multiprocessing.active_children()
	while num_running>0:	
		while results.empty():
			time.sleep(1.0)
			#active=multiprocessing.active_children()	# poll for active processes
		# at least one process has terminated
		while not results.empty():
			num_running += - 1
			(name, code) = results.get()
			#name = proverDict[name]		# mapping the number back to the real command name
			#print str(name) + " returned with " + str(code)
			
			#print name + " finished; positive returncodes are " + str(provers[name])
			r = reasoners.getByCommand(name)
			r.return_code = code
			if code in r.positive_returncodes:
				success = True
				if r.isProver():
					logging.getLogger(__name__).info(name + " found an proof/inconsistency")
				else:
					logging.getLogger(__name__).info(name + " found a counterexample/model")
				
					
		if success:
			# terminate all processes that are still active
			for p in multiprocessing.active_children():
				# TODO: want to gracefully shut down
				time.sleep(1.0)
				terminateSubprocess(p)
		break


	return reasoners

		#num_running = len(active)
#		print(str(num_running) + " active processses")
#		time.sleep(0.5)
#		for p in reasonerProcesses:
#			if p not in active:
#				print p
#				if p.returncode in p.provers[p.name()]:
#					success = True
#		for p in finderProcesses:
#			if p not in active:
#				print p
#				if p.returncode in p.finders[p.name()]:
#					success = True

#	for r in reasonerProcesses:
#		provers[r.name()]=r.returncode
#	for finder in finderProcesses:
#		modelfinders[finder.name()]=find.returncode
