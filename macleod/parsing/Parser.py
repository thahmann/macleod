import argparse

import ply.lex as lex
import ply.yacc as yacc

import macleod.logical.Logical as Logical
import macleod.logical.Connective as Connective
import macleod.logical.Symbol as Symbol
import macleod.logical.Quantifier as Quantifier
import macleod.logical.Negation as Negation

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

def t_error(t):
    raise TypeError("Unknown text '%s'" % (t.value,))

t_URI = r"http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_NONLOGICAL = r'[\w\-=]+'
t_ignore = " \t\n"
t_COMMENT = r'\/\*[\w\W\d*]+?\*\/'
t_STRING = r"'(.+?)'"

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
    #if len(p) == 1:
    #    # the empty string means there are no atomic symbols
    #    p[0] = []
    #else:
    #    p[0] = p[4]
    pass

def p_statement(p):
    """
    statement : axiom statement
    statement : import statement
    statement : comment statement
    statement : comment
    statement : axiom
    statement : statement
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

    p[0] = p[3]

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
    parameter : function 
                | nonlogicals
    """

    if len(p) == 3:
        parameters = [p[1]]
        parameters.append(p[2])
        p[0] = parameters
    else:
        p[0] = p[1]


def p_function(p):
    """
    function : LPAREN NONLOGICAL nonlogicals RPAREN
    """

    p[0] = Symbol.Function(p[2], [p[3]])

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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Testing')
    parser.add_argument('-f', '--file', type=str, help='file', required=True)
    args = parser.parse_args()

    with open(args.file, 'r') as f:
        buff = f.read()

    lex.lex()


    #lex.input(buff)
    #for tok in iter(lex.token, None):
    #    print(repr(tok.type), repr(tok.value))

    yacc.yacc()
    yacc.parse(buff, debug=True)
