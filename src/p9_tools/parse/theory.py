import os


def concatenate_axioms(lines):
    # remove specific lines
    [lines.remove(x) for x in lines if "formulas(assumptions)" in x]
    [lines.remove(y) for y in lines if "end_of_list" in y]

    # put axioms together into one list
    index_last_line = []
    for c, val in enumerate(lines):
        if "." in val:
            index_last_line.append(c)

    one_axiom = []
    all_axioms = []
    c2 = 0
    for c1, i in enumerate(index_last_line):
        while c2 <= i:
            one_axiom.append(lines[c2])
            c2 += 1
        all_axioms.append("".join(one_axiom))
        one_axiom.clear()

    return all_axioms


def replace_symbol(lines, symbol, new_symbol):
    for x, line in enumerate(lines):
        while symbol in lines[x]:
            lines[x] = line.replace(symbol, new_symbol)
    return lines


def theory_setup(theory_name):
    with open(theory_name, "r") as f:
        lines = f.readlines()
        lines = concatenate_axioms(lines)
        # remove comments
        for x, line in enumerate(lines):
            while "%" in lines[x]:
                lines.remove(lines[x])

        try:
            while True:
                lines.remove("\n")
        except ValueError:
            pass
        replace_symbol(lines, ".", "")      # added this for definitions
        replace_symbol(lines, ".\n", "")
        replace_symbol(lines, "\t", "")
    f.close()
    return lines


# function to identify the definitions required to pull from
# parsing all the signatures that appear before an opening parentheses
def signatures(lines):
    s = set()
    primitives = ["leq"]

    for axiom in lines:
        for i, char in enumerate(axiom):
            if char == "(" and axiom[i-1].isalpha():
                j = i-1
                signature = ""
                # accounts for signatures containing letters, numbers and underscores
                while (axiom[j].isalpha() or axiom[j].isnumeric() or axiom[j] == "_") and j >= 0:
                    signature = axiom[j] + signature    # appending letter to the front of string
                    j -= 1
                if signature and signature not in primitives:
                    s.add(signature)
    return s


# retrieve definitions given relation signatures
def definitions(signature, path=None):
    file_name = str(signature) + ".in"
    lines = []

    for definition_file in os.listdir(path):
        if definition_file == file_name:
            lines = theory_setup(path + "/" + definition_file)

    return lines




