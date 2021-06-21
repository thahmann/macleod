from p9_tools import config
from p9_tools.parse import theory
from p9_tools.relationship import relationship
from p9_tools.insertion import remove_duplicate_chains

import pandas as pd


def insertion(chain, in_chain, new_t=config.new_t, file_path=config.path, definitions_path=config.definitions):
    top = []       # theories that entail theory
    bottom = []    # theories entailed by new theory

    insert = True               # flag for insertion in existing chain
    location = len(in_chain)    # default location at end of list
    found = False

    for i, t in enumerate(in_chain):
        rel = relationship.main(new_t, t, True, file_path, definitions_path)

        if rel == "entails_t1_t2":
            bottom.append(chain[i])

        elif "equivalent" in rel:
            # theory already exists in the chain
            if new_t == t:
                return True
            # there is an equivalent theory
            else:
                bottom.append(chain[i])

        elif rel == "entails_t2_t1":
            top.append(chain[i])
            # insertion location
            if not found:
                location = i
                found = True

        # if there is no entailment for any theory, do not insert and create a new chain
        else:
            insert = False

    new_t = new_t.replace(".in", "")
    if insert:
        # new theory can be inserted to this chain

        chain.insert(location, new_t)
        return True
    else:
        # form new chain with select theories
        if bottom or top:
            new_chain = bottom + [new_t] + top
            return new_chain
        # no entailment for any theories in the chain
        else:
            return False


def find_position(chain, low, high, new_t=config.new_t, insert=False,
                  file_path=config.path, definitions_path=config.definitions):
    if low == high:
        compare_low = relationship.main(new_t, chain[low], insert, file_path, definitions_path)
        if compare_low == "entails_t1_t2":
            return low + 1
        elif compare_low == "entails_t2_t1":
            return low
        else:
            return -1

    if low > high:
        return low

    mid = (low+high)//2
    compare_mid = relationship.main(new_t, chain[mid], insert, file_path, definitions_path)

    # middle value
    if "equivalent" in compare_mid:
        # theory already exists in the chain. only the names are checked (not the contents/axioms)
        if new_t == chain[mid]:
            return -1
        # found an equivalent theory
        else:
            if insert:
                return mid
            else:
                return chain[mid]
    # lower half
    elif compare_mid == "entails_t2_t1":
        return find_position(chain, low, mid-1, new_t, insert, file_path, definitions_path)
    # upper half
    elif compare_mid == "entails_t1_t2":
        return find_position(chain, mid+1, high, new_t, insert, file_path, definitions_path)
    # does not belong
    else:
        return -1


def search(in_chain, new_t=config.new_t, file_path=config.path, definitions_path=config.definitions):
    location = find_position(in_chain, 0, len(in_chain)-1, new_t, file_path, definitions_path)
    if not isinstance(location, int):
        print("an equivalent theory is ", location)
    else:
        print("no equivalent theory found")


def main(csv_file=config.csv, new_t=config.new_t, function=config.function,
         file_path=config.path, definitions_path=config.definitions, hierarchy=False):
    # open existing chain decomposition file, converted to DataFrame then lists
    chains_df = pd.read_csv(csv_file)
    chains_list = []
    [chains_list.append(row) for row in chains_df]
    chains_list = chains_df.values.tolist()

    for i, c in enumerate(chains_list):
        chains_list[i] = list(filter(lambda a: pd.notna(a), c))

    # add ".in" suffix to theories in chains to match input file names to check relationships
    input_chains = [[str(s) + ".in" for s in c] for c in chains_list]

    inserted = False

    # first check if new theory is consistent
    try:
        with open(new_t, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("theory '" + new_t + "' not found")
        return
    lines = theory.concatenate_axioms(lines)
    theory.replace_symbol(lines, ".\n", "")
    theory.replace_symbol(lines, "\t", "")
    check_consistent = relationship.consistency(lines, [])

    if check_consistent is not True:
        print("your theory is inconsistent")
    else:

        print("original\n", chains_list)

        # update each existing chain
        # will not need to do insertions for new chains created that already contain added theory
        num_chains_start = len(chains_list)

        for i, chain in enumerate(chains_list[:num_chains_start]):

            if function == 1:   # insertion
                insertion_results = insertion(chain, input_chains[i], new_t, file_path, definitions_path)

                # new chain was created
                if isinstance(insertion_results, list):
                    new_chain = insertion_results
                    # print(new_chain)

                    chains_list.append(new_chain)

                    new_chain = [str(c) + ".in" for c in new_chain]
                    input_chains.append(new_chain)

                    inserted = True

                # theory was inserted into the chain
                elif insertion_results:
                    inserted = True

            elif function == 2:  # search for an equivalent theory
                print(search(input_chains[i], new_t, definitions_path))

        # new theory has not been inserted anywhere. create a new chain
        # this shouldn't happen after full construction of the hierarchy; if the new theory
        # is inconsistent with the root, it doesn't belong in the hierarchy
        if inserted is False and hierarchy:
            new_t = new_t.replace(".in", "")
            chains_list.append([new_t])
            input_chains.append([new_t + ".in"])

        # remove duplicate chains
        remove_duplicate_chains.removals(chains_list)

        print("here is the final list \n", chains_list)

        new_df = pd.DataFrame(chains_list)
        new_df.to_csv(csv_file, mode="w", index=False)
        print("chain decomposition is now updated")


if __name__ == "__main__":
    main()
