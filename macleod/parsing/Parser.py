import argparse
import logging
import os
import ply.lex as lex
import ply.yacc as yacc
import re

from pathlib import Path

import macleod.Ontology as Ontology
from macleod.Ontology import pretty_print
import macleod.logical.Logical as Logical
import macleod.logical.Connective as Connective
import macleod.logical.Logical as Logical
import macleod.logical.Negation as Negation
import macleod.logical.Quantifier as Quantifier
import macleod.logical.Symbol as Symbol

LOGGER = logging.getLogger(__name__)

tokens = (
    "LPAREN",
    "RPAREN",
    "NOT",
    "AND",
    "OR",
    "EXISTS",
    "FORALL",
    "IFF",
    "IF",
    "URI",
    "COMMENT",
    "CLCOMMENT",
    "STRING",
    "START",
    "IMPORT",
    "NONLOGICAL"
)

precedence = (('left', 'IFF'),
              ('left', 'IF'))

def t_NOT(t): r'not'; return t
def t_AND(t): r'and'; return t
def t_OR(t): r'or'; return t 
def t_EXISTS(t): r'exists'; return t
def t_FORALL(t): r'forall'; return t
def t_IFF(t): r'iff'; return t
def t_IF(t): r'if'; return t
def t_CLCOMMENT(t): r'cl-comment'; return t
def t_START(t): r'cl-text'; return t
def t_IMPORT(t): r'cl-imports'; return t
def t_LPAREN(t): r'\('; return t
def t_RPAREN(t): r'\)'; return t

def t_error(t):
    raise TypeError("Unknown text '%s'" % (t.value,))

t_URI = r"http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$\=\?\/\%\-_@.&+]|[!*,]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
t_NONLOGICAL = r'[<>=\w\-=]+'
t_COMMENT = r'\/\*[\w\W\d*]+?\*\/'
t_STRING = r"'(.+?)'"
t_ignore = " \r\t\n"

def p_stater(p):
    """
    starter : COMMENT ontology
    starter : ontology
    """

    if len(p) == 3:

        p[0] = p[2]

    else:

        p[0] = p[1]

def p_ontology(p):
    """
    ontology : LPAREN START URI statement RPAREN
    ontology : statement
    """
    if len(p) == 6:

        p[0] = p[4]

    else:

        p[0] = p[1]

def p_statement(p):
    """
    statement : axiom statement
    statement : import statement
    statement : comment statement
    statement : axiom
    statement : import
    statement : comment
    """

    if len(p) == 3:

        statements = [p[1]]

        if isinstance(p[2], list):
            statements += p[2]
        else:
            statements.append(p[2])

        p[0] = statements

    else:

        p[0] = [p[1]]

def p_comment(p):
    """
    comment : LPAREN CLCOMMENT STRING RPAREN
    """

    #p[0] = p[3]
    p[0] = None
    

def p_import(p):
    """
    import : LPAREN IMPORT URI RPAREN
    """

    p[0] = p[3]

def p_axiom(p):
    """
    axiom : negation
          | universal
          | existential
          | conjunction
          | disjunction
          | conditional
          | biconditional
          | predicate
    """

    p[0] = p[1]



def p_negation(p):
    """
    negation : LPAREN NOT axiom RPAREN
    """

    p[0] = Negation.Negation(p[3])


def p_conjunction(p):
    """
    conjunction : LPAREN AND axiom_list RPAREN
    """

    p[0] = Connective.Conjunction(p[3])

def p_disjunction(p):
    """
    disjunction : LPAREN OR axiom_list RPAREN
    """

    p[0] = Connective.Disjunction(p[3])

def p_axiom_list(p):
    """
    axiom_list : axiom axiom_list
    axiom_list : axiom
    """

    if len(p) == 3:

        axioms = [p[1]]

        if isinstance(p[2], list):
            axioms += p[2]
        else:
            axioms.append(p[2])

        p[0] = axioms

    else:

        p[0] = [p[1]]

def p_conditional(p):
    """
    conditional : LPAREN IF axiom axiom RPAREN
    """

    p[0] = Connective.Disjunction([Negation.Negation(p[3]), p[4]])


def p_biconditional(p):
    """
    biconditional : LPAREN IFF axiom axiom RPAREN
    """

    p[0] = Connective.Conjunction([Connective.Disjunction([Negation.Negation(p[3]), p[4]]),
                                   Connective.Disjunction([Negation.Negation(p[4]), p[3]])
                                  ])

def p_existential(p):
    """
    existential : LPAREN EXISTS LPAREN nonlogicals RPAREN axiom RPAREN
    """

    p[0] = Quantifier.Existential(p[4], p[6])

def p_universal(p):
    """
    universal : LPAREN FORALL LPAREN nonlogicals RPAREN axiom RPAREN
    """

    p[0] = Quantifier.Universal(p[4], p[6])


def p_predicate(p):
    """
    predicate : LPAREN NONLOGICAL parameter RPAREN
    """

    p[0] = Symbol.Predicate(p[2], p[3])

def p_parameter(p):
    """
    parameter : function parameter
    parameter : nonlogicals parameter
    parameter : function
    parameter : nonlogicals
    """

    if len(p) == 3:

        if isinstance(p[1], list):
            parameters = p[1]
            if isinstance(p[2], list):
                parameters += p[2]
            else:
                parameters.append(p[2])
        else:
            parameters = [p[1]]
            if isinstance(p[2], list):
                parameters += p[2]
            else:
                parameters.append(p[2])

        p[0] = parameters

    else:

        if isinstance(p[1], list):
            p[0] = p[1]
        else:
            p[0] = [p[1]]


def p_function(p):
    """
    function : LPAREN NONLOGICAL parameter RPAREN
    """

    p[0] = Symbol.Function(p[2], p[3])

def p_nonlogicals(p):
    """
    nonlogicals : NONLOGICAL nonlogicals
    nonlogicals : NONLOGICAL
    """

    if len(p) == 3:

        nonlogicals = [p[1]]

        if isinstance(p[2], list):
            nonlogicals += p[2]
        else:
            nonlogicals.append(p[2])

        p[0] = nonlogicals

    else:

        p[0] = [p[1]]


def p_error(p):
    print("Welp this is confusing", p.lineno, p.lexpos)
    raise TypeError("unknown text at %r" % (p.value,))

def parse_file(path, sub, base, resolve=False):
    """
    Accepts a path to a Common Logic file and parses it to return an Ontology object.

    :param String path, path to common logic file
    :return Ontology onto, newly constructed ontology object
    """

    if not os.path.isfile(path):
        LOGGER.warning("Attempted to parse non-existent file: " + path)

    with open(path, 'r') as f:
        buff = f.read()

    lex.lex(reflags=re.UNICODE)
    yacc.yacc()

    parsed_objects = yacc.parse(buff)

    ontology = Ontology(path)
    ontology.basepath = (sub, base)

    for logical_thing in parsed_objects:

        if isinstance(logical_thing, Logical.Logical):

            ontology.add_axiom(logical_thing)

        elif isinstance(logical_thing, str):

            ontology.add_import(logical_thing)

    if resolve:

        ontology.resolve_imports(resolve)

    return ontology

if __name__ == '__main__':

    # Support conditional parameters
    import sys

    parser = argparse.ArgumentParser(description='Utility function to read and translate Common Logic Interchange Format (.clif) files.')
    parser.add_argument('-f', '--file', type=str, help='Path to Clif file to parse', required=True)
    parser.add_argument('-p', '--ffpcnf', action="store_true", help='Automatically convert axioms to function-free prenex conjuntive normal form', default=False)
    parser.add_argument('--resolve', action="store_true", help='Automatically resolve imports', default=False)
    parser.add_argument('-b', '--base', required='--resolve' in sys.argv, type=str, help='Path to directory containing ontology files')
    parser.add_argument('-s', '--sub', required='--resolve' in sys.argv, type=str, help='String to replace with basepath found in imports')
    args = parser.parse_args()

    LOGGER.warning("DERP")
    ontology = parse_file(args.file, args.sub, args.base, args.resolve)
    pretty_print(ontology, args.ffpcnf)
