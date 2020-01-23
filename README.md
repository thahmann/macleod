Macleod
======================================================

Installation
------------

## Dependencies

At the moment, pyparsing is still required: <https://pypi.python.org/pypi/pyparsing>, though the project is moving away from it (e.g. clif_converter.py no longer needs it and translates CLIF files to TPTP much more efficiently now).

The following dependencies are required:

* ply
* pyparsing
* texttable
* owlready (only for conversion to OWL)
* PyQt5 (only for the GUI in macleod/gui/gui_main.py)

This is most easily obtained with <code>sudo pip install [library]</code> (may need administrator rights)

### Windows:

For Windows, in addition to the above dependencies, the following additional dependencies are required:
* pywin32 <https://github.com/mhammond/pywin32/releases>
* wmi <http://timgolden.me.uk/python/wmi/index.html>

Again, they are most easily obtained via the command  <code> pip install [library]</code> 



Quick Start
-----------
* Install required dependencies (see above)
* Create a macleod folder in your home directory
* Place copies of the theorem provers and model finders in your newly created macleod folder or whereever you want them to reside
* Copy logging.conf to that folder and edit the following setting therein to point to where you would like all logging to be located. Here an example for a directory (relative to the home directory) on Windows):
[handler_fHandler]
args = ('macleod/macleod.log',)
* Copy macleod_win.conf (or macleod_mac.conf or macleod_linux.conf, depending on your operating system) to the newly created macleod folder and edit the paths that point to your local ontology directory and the reasoners (theorem provers and model finders) as necessary, e.g. on Windows:
[system]
path: GitHub/colore/ontologies/
* For convenience you should add the macleod/ and bin/ folders to your python path

About the project:
------------------

This program consists of a set of scripts designed for key reasoning tasks frequently encountered in ontology design and verification. At the moment it focuses on automating tasks that can be accomplished independent of the semantic of concepts and relations. These tasks are consistency checking of ontologies and their modules as well as checking whether competency questions, providing as ''lemmas'', are entailed.

While the program primarily targets first-order ontologies specified in the Common Logic (CL) syntax, some parts of it can also be used for reasoning about ontologies in LADR (Prover9/Mace4) or TPTP syntax (accepted by many first-order theorem provers and model finders, including Vampire, IProver and Paradox). The tasks are accomplished by running existing automated theorem provers and model finders in parallel to establish consistency or inconsistency of an ontology or a module thereof, or to prove a sentence from an ontology (or module) or to find a counterexample of the sentence.
Moreover, the tool exploits the modularity of ontologies, which manifests itself in its file CL imports structure. 


GUI:
---- 
* Navigate to the gui subfolder
* Execute the gui_alpha.py file with python


In the near future it will be integrated with COLORE to provide design, verification, and other reasoning support for all ontologies in the repository.

Troubleshooting:
----------------

certain errors (for example "bad magic number in 'macleod': b'\x03\xf3\r\n': ImportError") that appear after updating the repository locally can be fixed by deleting the Python cache for the macleod directory. This can be accomplished with the command "find . -name \*.pyc -delete"
