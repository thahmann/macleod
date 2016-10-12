if __name__ == '__main__':
    import os, sys

    for root, dirs, files in os.walk(sys.argv[1]):
        for f in files:
            fullpath = os.path.join(root, f)
            if (fullpath.endswith('.out') 
                or fullpath.endswith('.p9') 
                or fullpath.endswith('.tptp') 
                or fullpath.endswith('.p9i') 
                or fullpath.endswith('.p9.clif')
                or fullpath.endswith('options.txt')):
                os.remove(fullpath)

