Macleod
======================================================

About the project:
------------------

This program consists of a set of scripts designed for key reasoning tasks frequently encountered when desiging and verifying (testing) ontologies written in the CLIF dialect of the Common Logic standard. Note that the program currently supports only a limited subset of the full semantics of Common Logic: it only supports the standard logical connectives (if, iff, and, or, not) and quantifiers (exists, forall) for writing first-order logic axioms and unrestricted importation of the axiom from another CLIF file. It does not support other module semantics  and syntactic sugar like sequence markers. 

The most common tasks supported at the moment:
* Translating a single CLIF file (a "module") or a CLIF ontology (a single CLIF file and its import closure) to formats supported by FOL reasoners: 
** TPTP, which is supported by all reasoners participating in the annual theorem proving competition (ATP) including Vampire and the model finder Paradox 
** LADR, which is supported by the theorem prover Prover9 and its accompanying model finder Mace4
* Extracting an OWL approximation of a CLIF ontology or module 
* Verifying the logical consistency of a CLIF ontology or module by invoking a model finder like Mace4 or Paradox
* Verifying the *non-trivial* logical consistency of a CLIF ontology or module by adding existential statements that demand the existence and non-existence of each new concept and relation for some individuals
* Proving theorems/lemmas that encode intended consequences of an ontology or module, such as properties of concepts and relations or competency questions

The program provides reusable functionality to parse CLIF files and represents them using an internal data structure that captures the logic of FOL. This structure can be further manipulated (e.g. converted into normal forms like CNF or PNF) and translated into various other syntaxes (such as TPTP or OWL). 

The reasoning tasks are accomplished by running existing automated theorem provers and model finders in parallel to establish consistency or inconsistency of an ontology or module, or to prove a sentence from an ontology (or module) or to find a counterexample of the sentence. Note that the reasoners are external to Macleod, they are called via the command line. For licencing reasons, they are not distributed with Macleod and must be installed separately as outlined in the installation instructions (many are available as pre-compiled binaries).


Installation
------------

Requirements: 
* Python 3.7.* or higher (there are some issues with Python 3.6.*)
* Virtual Environments for Python enabled, if not (or unsure) first run "pip install virtualenv"

It is recommended to create a virtual environment to work out of:

```bash
# On Windows hosts with Python3 already installed and on the %PATH%
# Create a new virtual environment called "ve" (or whatever you want to name it)
python -m venv ve
# Activate the newly created virtual environment
ve/scripts/activate.bat
```

```bash
# On Linux hosts with Python3 installed
python3 -m ve && . ve/bin/active
```

Once the virtual environment has been created and activated clone this repository and install:

```bash
# Clone the repository using https or ssh
git clone https://github.com/thahmann/macleod.git
# Go to the folder that contains the cloned repository,
# e.g. "%USERPROFILE%\GitHub\macleod\" by default on Windows hosts,
# or a location like "/home/git/macleod" on Linux hosts
cd macleod

# Install macleod and all dependencies via pip
pip install .

# Optionally you can install the GUI components as well (see more information about the GUI alpha version below)
pip install .[GUI]
```

As a next step, the configuration files need to be put in place:

```bash
# On Windows hosts:
# Go to your home directory and create a subfolder `macleod'
cd %USERPROFILE%
mkdir macleod
cd macleod
# copy the configuration files from the github folder to this new folder 
copy "%USERPROFILE%\GitHub\macleod\conf\macleod_win.conf .
copy "%USERPROFILE%\GitHub\macleod\conf\logging.conf .
```


```bash
# On Linux hosts:
# Go to your home directory and create a subfolder `macleod'
cd ~
mkdir macleod
cd macleod
# copy the configuration files from the github folder to this new folder 
cp "/home/git/macleod/conf/macleod_linux.conf .
cp "/home/git/macleod/conf/logging.conf .
```

In a final step, add the binaries of the theorem provers and model finders to be used for ontology verification and proving of lemmas to the "macleod" directory and edit the configuration file "maleod_win", "macleod_linux" or "macleod_mac" as necessary. In particular the commands for the utilized theorem provers and model finders must use the correct paths (if not on the PATH variable) and commands. Likewise, make sure that in *logging.conf* the *args* parameter of the section *[handler_fHandler]* uses the correct path for your host.

*Note: The provers are not needed for translation to TPTP, LADR or for extraction of OWL ontologies.*


Usage
-----

After macleod is installed a number of scripts will be available to run from within the virtual environment:

```bash
[rob@demo]$ parse_clif -f ../colore/ontologies/multidim_space_codib/codib_down.clif 
∀(x)[(~(S(x) & ~ZEX(x)) | ∃(y)[(P(y,x) & Min(y))])]
∀(x,y)[(~(S(x) & S(y) & BCont(x,y)) | (Cont(x,y) & Inc(x,y)))]
∀(x,y,v,z)[(~(S(x) & S(y) & S(v) & S(z) & SC(x,y) & Min(x) & P(x,v) & Cont(y,v) & Cont(z,x) & Cont(z,y)) | BCont(z,x))]
∀(x,y,z,v)[(~(S(x) & S(y) & S(v) & S(z) & SC(x,y) & P(x,v) & P(y,v) & Cont(z,x) & Cont(z,y) & Covers(v,z)) | ~BCont(z,v))]
∀(x,y,z)[(~(S(x) & S(y) & S(z) & BCont(x,y) & P(y,z) & ∀(v,w)[(~(S(v) & S(w) & P(v,z) & ~PO(v,y) & P(w,x)) | ~Cont(w,v))]) | BCont(x,z))]
∀(x,y,z)[(~(S(x) & S(y) & S(z) & BCont(x,y) & Cont(z,x)) | BCont(z,y))]
∀(x,y)[((~(S(x) & S(y) & BCont(x,y)) | (S(x) & S(y) & ~ZEX(x) & ∀(z)[(~(P(z,x) & Min(z)) | BCont(z,y))])) & (~(S(x) & S(y) & ~ZEX(x) & ∀(z)[(~(P(z,x) & Min(z)) | BCont(z,y))]) | (S(x) & S(y) & BCont(x,y))))]

# To launch the GUI
[rob@demo]$ macleod
```

To check the consistency of modules you will need to place the prover executables into the provers/ sub-directory. Once you have the provers in the correct directory edit the configuration file for your platform within the conf/ sub-directory. 


Troubleshooting:
----------------

certain errors (for example "bad magic number in 'macleod': b'\x03\xf3\r\n': ImportError") that appear after updating the repository locally can be fixed by deleting the Python cache for the macleod directory. This can be accomplished with the command "find . -name \*.pyc -delete"


GUI:
----

The GUI is currently in alpha state and might even be broken due to recent changes in other components of macleod.
The main capabilities (when working) of the GUI are:
* open an ontology (a clif file) and visualize all its imports
* execute basic tasks (verification, conversion to LADR, TPTP)
