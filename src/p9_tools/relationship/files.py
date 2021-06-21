import os


def create_file(name, contents, path):
    new_path = os.path.join(path, name)
    with open(new_path, "w+") as new_file:
        new_file.write(contents)


# update owl files
def owl(t1, rel, t2, alt_file, meta_file):
    l1 = "ObjectPropertyAssertion(:" + rel
    l2 = " :" + t1 + " :" + t2 + ")\n\n"
    syntax1 = l1 + l2

    f = open(alt_file, "r")
    alt_lines = f.readlines()
    f.close()

    for c1 in range(len(alt_lines)-1, 0, -1):
        if alt_lines[c1] != "":
            alt_lines.insert(c1, syntax1)
            break

    f = open(alt_file, "w")
    alt_string = "".join(alt_lines)
    f.write(alt_string)
    f.close()

    l3 = "Declaration(NamedIndividual(:" + t1 + "))\n"

    l4 = "# Individual: :" + t1 + " (:" + t1 + ")\n\n"
    l5 = "ClassAssertion(:Theory :" + t1 + ")\n\n"

    l6 = "# Individual: :" + t2 + " (:" + t2 + ")\n\n"
    l7 = "ClassAssertion(:Theory :" + t2 + ")\n"

    l8 = "ObjectPropertyAssertion(:" + rel + " :" + t1 + " :" + t2 + ")\n\n"
    syntax2 = l4 + l5 + l6 + l7 + l8

    f = open(meta_file, "r")
    meta_lines = f.readlines()
    f.close()

    for c, l in enumerate(meta_lines):
        if l3 in l:
            break
        elif "###" in l:
            meta_lines.insert(c, l3)
            break
    for c1 in range(len(meta_lines)-1, 0, -1):
        if meta_lines[c1] != "":
            meta_lines.insert(c1, syntax2)
            break

    f = open(meta_file, "w")
    meta_string = "".join(meta_lines)
    f.write(meta_string)
    f.close()


def check(meta_file, t1, t2):
    # check if relationship has been found already
    possible = ["inconclusive",
                "consistent",
                "inconsistent",
                "entails",
                "independent",
                "equivalent"]

    with open(meta_file, "r") as file3:
        all_relations = file3.readlines()
        for r in all_relations:
            for p in possible:
                if "ObjectPropertyAssertion(:" + p + " :" + t1 + " :" + t2 + ")" in r:
                    # print("ObjectPropertyAssertion(:" + p + " :" + t1 + " :" + t2 + ")")
                    relationship = p + "_t1_t2"
                    file3.close()
                    return relationship
                elif "ObjectPropertyAssertion(:" + p + " :" + t2 + " :" + t1 + ")" in r:
                    # print("ObjectPropertyAssertion(:" + p + " :" + t2 + " :" + t1 + ")")
                    relationship = p + "_t2_t1"
                    file3.close()
                    return relationship
    file3.close()
    # nf = not found
    return "nf"

