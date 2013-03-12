'''
Created on 2012-11-20

@author: Torsten Hahmann
'''

import os, sys, signal


class Process(object):
    
    # terminate a process
    # needed for downwards compatibility with Python 2.5
    @staticmethod
    def terminate (process):
        def terminate_win (process):
            return win32process.TerminateProcess(process._handle, -1)
    
        def terminate_nix (process):
            #os.kill(process.pid, signal.SIGINT)
            return os.killpg(process.pid, signal.SIGINT)
            #return os.waitpid(process.pid, os.WNOHANG)
    
        terminate_default = terminate_nix
    
        handlers = {
            "win32": terminate_win, 
            "linux2": terminate_nix
        }
    
        return handlers.get(sys.platform, terminate_default)(process)
