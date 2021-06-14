# remove duplicate chains in chain decomposition
def duplicate_check(short, long):
    # check if two chains are duplicates
    # duplicate = if one chain is 'subset' of another

    # index of theory being checked in the shorter chain
    i = 0

    # check if each theory in short chain exists in long
    for t in long:
        if t == short[i]:
            i+=1
            # reached end of short chain, all theories in short found in long
            if i == len(short):
                # chains are duplicates
                return True

    return False


def removals(chains_list):
    indices = set()

    # chain # being checked against all subsequent
    # chain "x"
    # no need to check previous, comparisons done already

    chain_slice = list(chains_list[:len(chains_list)-1])

    for i, x in enumerate(chain_slice):
        # all subsequent chains
        for j, c in enumerate(list(chains_list[i+1:])):
            # assign short and long chain indices
            if len(x) <= len(c):
                short = i
                long = j + (i+1)
            else:
                short = j + (i+1)
                long = i
            if duplicate_check(chains_list[short], chains_list[long]):
                indices.add(short)

    for i in sorted(indices, reverse=True):
        chains_list.pop(i)

