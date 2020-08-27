Macleod
======================================================

Installation
------------

It is recommended to create a virtual environment to work out of:

```bash
# On Windows hosts with Python3 already installed and on the %PATH%
python -m venv ve && virtual_env/scripts/activate.bat

# On Linux hosts with Python3 installed
python3 -m ve && . ve/bin/active
```

Once the virtual environment has been created and activated clone this repository and install:

```bash
# Clone the repository using https or ssh
git clone https://github.com/thahmann/macleod.git && cd macleod

# Install macleod and all dependencies via pip
pip install .

# Optionally you can install the GUI components as well
pip install .[GUI]
```

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

About the project:
------------------

This program consists of a set of scripts designed for key reasoning tasks frequently encountered in ontology design and verification. At the moment it focuses on automating tasks that can be accomplished independent of the semantic of concepts and relations. These tasks are consistency checking of ontologies and their modules as well as checking whether competency questions, providing as ''lemmas'', are entailed.

While the program primarily targets first-order ontologies specified in the Common Logic (CL) syntax, some parts of it can also be used for reasoning about ontologies in LADR (Prover9/Mace4) or TPTP syntax (accepted by many first-order theorem provers and model finders). The tasks are accomplished by running existing automated theorem provers and model finders in parallel to establish consistency or inconsistency of an ontology or a module thereof, or to prove a sentence from an ontology (or module) or to find a counterexample of the sentence.
Moreover, the tool exploits the modularity of ontologies, which manifests itself in its file CL imports structure. 

In the near future it will be integrated with COLORE to provide design, verification, and other reasoning support for all ontologies in the repository.

Troubleshooting:
----------------

certain errors (for example "bad magic number in 'macleod': b'\x03\xf3\r\n': ImportError") that appear after updating the repository locally can be fixed by deleting the Python cache for the macleod directory. This can be accomplished with the command "find . -name \*.pyc -delete"

