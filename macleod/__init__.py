import logging
from pathlib import Path

from .ClifModule import *
from .ClifModuleSet import *
from .ClifLemmaSet import *
from .ReasonerSet import *
from .Reasoner import *
from .Clif import *
from .Commands import *
from .Ladr import *
from .Filemgt import *
from .Process import *
from .Ontology import *

# Setup our package level logger
logging.config.fileConfig(str(Path.home().joinpath('macleod').joinpath('logging.conf')))

__all__ = ["Ontology", "filemgt", "commands", "clif", "ladr", "process", "ReasonerSet", "Reasoner", "ClifModule", "ClifModuleSet", "ClifLemmaSet"]
