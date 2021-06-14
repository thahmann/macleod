from p9_tools.parse import theory


def extract_constants(lines):
    unique_constants = []
    for line in lines:
        if "(" in line:
            for c in range(line.index("(")+1, line.index(")")-1, 1):
                while line[c] != "," and line[c] not in unique_constants:
                    unique_constants.append(line[c])
    return unique_constants


def make_inequalities(unique_constants):
    pairs = []

    # find all unique pairs
    for i in range(0, len(unique_constants)-1, 1):
        for j in range(i+1, len(unique_constants), 1):
            pairs.append([unique_constants[i], unique_constants[j]])

    # create list of inequality statements with the pairs
    statements = []
    for pair in pairs:
        s = "\n" + pair[0] + "!=" + pair[1] + ".\n"
        statements.append(s)
    return statements


def model_setup(file_name):
    with open(file_name, "r+") as f:
        lines = f.readlines()
        input1 = (extract_constants(lines))
        add_these_lines = make_inequalities(input1)
        for line in add_these_lines:
            f.write(line)
    f.close()

    with open(file_name, "r") as f:
        model_spec_lines = f.readlines()
        # remove comments
        for x, line in enumerate(model_spec_lines):
            while "%" in model_spec_lines[x]:
                model_spec_lines.remove(model_spec_lines[x])
        try:
            while True:
                model_spec_lines.remove("\n")
        except ValueError:
            pass
        theory.replace_symbol(model_spec_lines, ".\n", "")
        theory.replace_symbol(model_spec_lines, "\t", "")
    f.close()
    return model_spec_lines

