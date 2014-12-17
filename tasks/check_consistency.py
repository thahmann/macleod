'''
Created on 2013-03-19

@author: Torsten Hahmann
'''

import sys
sys.path.append("../")

from tasks import *
from gui.Arborist import *
from src.ClifModuleSet import ClifModuleSet

import logging

def consistent(filename, options=[]):  
    m = ClifModuleSet(filename)
     
    #if '-module' in options:
    #    results = m.run_consistency_check_by_subset(abort=True, abort_signal=ClifModuleSet.CONSISTENT)
    #elif '-depth' in options:
    #    results = m.run_consistency_check_by_depth(abort=True, abort_signal=ClifModuleSet.CONSISTENT)
    #elif '-simple' in options:
    #    results = m.run_simple_consistency_check()
    #else:
    #    results = m.run_full_consistency_check(abort=True, abort_signal=ClifModuleSet.CONSISTENT)
    #    
    #if len(results)==0:
    #    logging.getLogger(__name__).info("+++ CONSISTENCY CHECK TERMINATED: NO MODULES FOUND IN " +str(m.get_imports()) +"\n")
    #else:
    #    for (r, value, _) in results:
    #        if value==-1:
    #            logging.getLogger(__name__).info("+++ CONSISTENCY CHECK TERMINATED: INCONSISTENCY FOUND IN " +str(r) +"\n")
    #            return (False, m)
    #    result_sets = [r[0] for r in results]
    #    result_sets.sort(lambda x,y: cmp(len(x), len(y)))
#   #     print result_sets[0]
#   #     print results
#   #     print "+++++" + str(value)
    #    if results[0][1]==1:
    #        logging.getLogger(__name__).info("+++ CONSISTENCY CHECK TERMINATED: PROVED CONSISTENCY OF " +str(result_sets[0]) +"\n")
    #        return (True, m)
    #    else:
    #        logging.getLogger(__name__).info("+++ CONSISTENCY CHECK TERMINATED: NO RESULT FOR CONSISTENCY OF " +str(result_sets[0]) +"\n")
    #        if len(result_sets)>1:
    #            for (r, value, _) in results:
    #                if value==1:
    #                    logging.getLogger(__name__).info("+++ CONSISTENCY CHECK TERMINATED: PROVED CONSISTENCY OF SUBONTOLOGY " +str(r[0]) +"\n")
    return (None, m)

def popup(event):
    men.post(event.x_root, event.y_root)

def derp():
    print 'derpy derpy'

if __name__ == '__main__':
    licence.print_terms()
    # global variables

    root = Tk()
    s = ttk.Style()
    s.theme_use('default')
    frame = Frame(root, width=500, height = 500)
    canvas = Canvas(frame, width = 600, height = 600)

    #men = Menu(root, tearoff=0)
    #men.add_command(label="See as root")
    #men.add_command(label="See as derp")
    #men.add_command(label="Work plz")

    #canvas.bind("<ButtonPress-2>", popup)



    canvas.pack(fill=BOTH, expand=1)
    frame.pack(fill=BOTH, expand=1)

    options = sys.argv
    options.reverse()
    options.pop()
    filename = options.pop()
    derp, clif = consistent(filename, options)

    arborist = VisualArborist(canvas)
    arborist.gather_nodes(clif)
    arborist.grow_tree()
    arborist.prune_tree(arborist.tree, None, 0)
    arborist.weight_tree()
    arborist.layout_tree()
    #arborist.dfs(arborist.tree, 0)
    arborist.draw_tree()

    root.mainloop()

    

