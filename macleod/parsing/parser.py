import logging
import os
import ply.lex as lex
import ply.yacc as yacc
import re

from pathlib import Path

import macleod.Ontology as Ontology
from macleod.logical.logical import Logical
from macleod.logical.connective import (Conjunction, Disjunction, Connective)
from macleod.logical.logical import Logical
from macleod.logical.negation import Negation
from macleod.logical.quantifier import (Universal, Existential, Quantifier)
from macleod.logical.symbol import (Function, Predicate)

LOGGER = logging.getLogger(__name__)

global parser 

class ParseError(Exception):
	pass

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
def t_NEWLINE(t): 
    r'\n+'
    t.lexer.lineno += len(t.value)
    

def t_error(t):
    raise TypeError("Unknown text '%s'" % (t.value,))

t_URI = r"http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$\=\?\/\%\-_@.&+]|[!*,]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
t_NONLOGICAL = r'[<>=\w\-=]+'
t_COMMENT = r'\/\*["\w\W\d*]+?\*\/'
t_STRING = r"['\"](.+)['\"]"
t_ignore = " \r\t"

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

    p[0] = Negation(p[3])


def p_conjunction(p):
    """
    conjunction : LPAREN AND axiom_list RPAREN
    """

    p[0] = Conjunction(p[3])

def p_disjunction(p):
    """
    disjunction : LPAREN OR axiom_list RPAREN
    """

    p[0] = Disjunction(p[3])

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

    p[0] = Disjunction([Negation(p[3]), p[4]])


def p_biconditional(p):
    """
    biconditional : LPAREN IFF axiom axiom RPAREN
    """

    p[0] = Conjunction([Disjunction([Negation(p[3]), p[4]]),
                                   Disjunction([Negation(p[4]), p[3]])
                                  ])

def p_existential(p):
    """
    existential : LPAREN EXISTS LPAREN nonlogicals RPAREN axiom RPAREN
    """

    p[0] = Existential(p[4], p[6])

def p_universal(p):
    """
    universal : LPAREN FORALL LPAREN nonlogicals RPAREN axiom RPAREN
    """

    p[0] = Universal(p[4], p[6])

def p_universal_error(p):
    """
    universal : LPAREN FORALL LPAREN nonlogicals RPAREN error axiom RPAREN
              | LPAREN FORALL LPAREN nonlogicals RPAREN error RPAREN
              | LPAREN FORALL LPAREN nonlogicals RPAREN axiom error RPAREN
              | LPAREN FORALL error LPAREN nonlogicals RPAREN error axiom RPAREN
    """

    raise ParseError("Error parsing term in Universal")


def p_predicate(p):
    """
    predicate : LPAREN NONLOGICAL parameter RPAREN
    """

    p[0] = Predicate(p[2], p[3])

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

    p[0] = Function(p[2], p[3])

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

    global parser

    # A little stack manipulation here to get everything we need
    stack = [symbol for symbol in parser.symstack][1:]
    print(stack)
    pivot = len(stack) - stack[::-1].index(next((x for x in stack[::-1] if x.type == 'axiom'), None))  
    current_axiom = stack[pivot:]
    current_axiom.append(p)

    # Use the brace level to figure out how many future tokens we need to complete the error token
    lparens = len([x for x in current_axiom if x.type == "LPAREN"])
    lookahead_tokens = []
    while lparens != 0:
        lookahead_token = parser.token()
        if lookahead_token == None:
            break
        else:
            lookahead_tokens.append(lookahead_token)
            if lookahead_token.type == "RPAREN": 
                lparens -= 1
            elif lookahead_token.type == "LPAREN":
                lparens += 1

    # Put together a full list of tokens for the error token
    current_axiom += lookahead_tokens

    # String manipulation to "underbar" the error token
    axiom_string = []
    overbar_error = ''.join([x+'\u0332' for x in p.value])
    p.value = overbar_error

    for token in current_axiom:
        raw_token = token.value
        if isinstance(raw_token, str):
            axiom_string.append(raw_token + ' ')
        elif isinstance(raw_token, list):
            for sub_token in raw_token:
                axiom_string.append(sub_token + ' ')

    print("""Error at line {}! Unexpected Token: '{}' :: "{}"\n\n{}""".format(p.lexer.lineno, p.value, ''.join(axiom_string), " ".join([symbol.type for symbol in parser.symstack][1:])))
    #return p



def parse_file(path, sub, base, resolve=False):
    """
    Accepts a path to a Common Logic file and parses it to return an Ontology object.

    :param String path, path to common logic file
    :return Ontology onto, newly constructed ontology object
    """

    print(path)

    global parser

    if not os.path.isfile(path):
        LOGGER.warning("Attempted to parse non-existent file: " + path)

    with open(path, 'r') as f:
        buff = f.read()

    lex.lex(reflags=re.UNICODE)
    parser = yacc.yacc()

    parsed_objects = yacc.parse(buff)

    ontology = Ontology(path)
    ontology.basepath = (sub, base)

    for logical_thing in parsed_objects:

        if isinstance(logical_thing, Logical):

            ontology.add_axiom(logical_thing)

        elif isinstance(logical_thing, str):

            ontology.add_import(logical_thing)

    if resolve:

        ontology.resolve_imports(resolve)

    return ontology

if __name__ == '__main__':

    LOGGER.error('This is not the droid you are looking for. Use bin/parser.py instead')
