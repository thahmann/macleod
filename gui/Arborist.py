#/usr/bin/python
"""
Class to manage the conversion from a clifModuleSet to a
more generic tree structure

@author Robert Powell
"""

from Tkinter import *
import ttk
from summary import *
import logging

LOG = logging.getLogger(__name__)

class Arborist(object):
    """ Arborist that can create trees """

    def __init__(self):
        """ Initialize an empty arborist """

        self.clif_set = None
        self.nodes = {}
        self.tree = None

    def get_object(self, module_name):
        """ Return the object of a module """

        return self.clif_set.get_import_by_name(module_name)

    def gather_nodes(self, clif_set):
        """ Create a dictionary of nodes from a ClifModuleSet """

        self.clif_set = clif_set
        for module in clif_set.imports:
            self.nodes[module.module_name] = Node(module)

    def grow_tree(self):
        """ Grow the tree by building the child/parent structure """

        self.tree = self.nodes[self.clif_set.module_name]
        for module in self.clif_set.imports:
            node = self.nodes[module.module_name]
            for parent_name in module.parents:
                parent = self.get_object(parent_name)
                parent_node = self.nodes[parent.module_name]
                node.parents.append(parent_node)
            for child_name in module.imports:
                child = self.get_object(child_name)
                child_node = self.nodes[child.module_name]
                node.children.append(child_node)

    def deep_clean(self):
        """ Fix the tree at last """

        removes = []
        for name in self.nodes:
            if 'definitions' in name:
                removes.append(name)

        for name, node in self.nodes.iteritems():
            if 'definition' not in name:
                node.children = [c for c in node.children if 'definitions' not in c.name]
                node.parents = [p for p in node.parents if 'definitions' not in p.name]
                for c in node.children:
                    if 'definitions' in c.name:
                        LOG.debug('Did not remove definition in ' + node.name)
                for p in node.parents:
                    if 'definitions' in p.name:
                        LOG.debug('Did not remove definition in ' + node.name)

        visited = self.traverse(self.tree)        

        for name, node in self.nodes.iteritems():
            if node not in visited:
                removes.append(name)

        for name in removes:
            try:
                self.nodes.pop(name)
            except KeyError:
                LOG.debug('Already removed definition ' + name)

    def traverse(self, rootnode):
        visited = [rootnode]
        thislevel = [rootnode]
        while thislevel:
            nextlevel = list()
            for n in thislevel:
                visited.append(n)
                if n.children: nextlevel += n.children
            print
            thislevel = nextlevel

        return visited

    def prune_tree_bfs(self, rootnode, depth):
        visited = [rootnode]
        thislevel = [rootnode]
        while thislevel:
            nextlevel = list()
            for n in thislevel:
                visited.append(n)

                # Establish upwards links in tree
                for child in n.children:
                    if n not in child.parents:
                        child.parents.append(n)

                n.depth = depth
                if n.children:
                    nextlevel += n.children
            depth += 1
            thislevel = nextlevel
        return visited


class VisualArborist(Arborist):
    """ Visual extension of the Arborist """

    def __init__(self, visualizer):
        """ Create a new VisualArborist """

        Arborist.__init__(self)
        self.visualizer = visualizer
        self.canvas = visualizer.canvas
        self.max_width = 1000
        self.selected_node = None


    def gather_nodes(self, clif_set):
        """ Create a dictionary of nodes from a ClifModuleSet """

        self.clif_set = clif_set
        for module in clif_set.imports:
            self.nodes[module.module_name] = VisualNode(module, self.visualizer, self)

    def weight_tree(self):
        """ Climb the tree and weight each level based on its children """

        nodes = sorted(self.nodes.values(), key=lambda n: n.depth, reverse=True)
        for node in nodes:
            node.set_visual_parent()
            node.set_visual_children()
            if len(node.visual_children) == 0:
                node.width = 40
            elif len(node.visual_children) == 1:
                node.width = node.visual_children[0].width
            else:
                # Don't count nodes own width
                for child in node.visual_children:
                    node.width += child.width

    # TODO Don't know if this belongs here
    def remove_tree(self):
        """ Remove the drawn elements of the tree from canvas """

        self.canvas.delete(ALL)

    def layout_tree(self):
        """ Layout the tree by setting the coordinates for each node """

        self.tree.x_pos = 0.5 * self.max_width
        self.tree.y_pos = 20

        levels = {}
        for node in sorted(self.nodes.values(), key=lambda n: n.depth):
            if node.depth in levels:
                levels[node.depth].append(node)
            else:
                levels[node.depth] = [node]

        for level_index in sorted(levels, key=lambda n: int(n)):
            level = sorted(levels[level_index], key=lambda n: n.width, \
                    reverse=True)

            for node in level:
                if node.visual_parent is not None:
                    if len(node.visual_parent.visual_children) == 1:
                        node.x_pos = node.visual_parent.x_pos
                    else:
                        if (len(node.visual_parent.visual_children) % 2 == 0):
                            node.x_pos = node.visual_parent.x_pos - \
                                    (0.5 * (node.visual_parent.width - 40)) + \
                                    node.visual_parent.offset
                        else:
                            node.x_pos = node.visual_parent.x_pos - \
                                    (0.5 * node.visual_parent.width) + \
                                    node.visual_parent.offset

                    node.visual_parent.offset += node.width
                    node.y_pos = node.visual_parent.y_pos + 40

    def draw_tree(self):
        """ Use Tkinter to draw the nodes on canvas """

        [node.draw() for node in self.nodes.values()]
        [node.draw_links() for node in self.nodes.values()]


class Node(object):
    """ Generic node object for the tree """

    def __init__(self, clif_module):
        """ Create a new node from a ClifModule """

        self.name = clif_module.module_name
        self.parents = []
        self.children = []
        self.definitions = {'parents':[], 'children':[]}
        self.depth = clif_module.depth
        self.greatest_depth = 0
        self.duplicate = False


class VisualNode(Node):
    """ The visual extension of the Node """

    def __init__(self, clif_module, visualizer, owner):

        Node.__init__(self, clif_module)
        self.module = clif_module
        self.canvas = visualizer.canvas
        self.visualizer = visualizer
        self.menu = Menu(self.canvas, tearoff=0)
        self.box = None
        self.x_pos = 0
        self.y_pos = 0
        self.visual_parent = None
        self.visual_children = []
        self.width = 0
        self.offset = 0
        self.information = {}
        self.child_links = []
        self.parent_links = []
        self.drawn_hidden = False
        self.owner = owner

    def show_popup(self, event):
        """ Display the context menu for the node """

        self.menu.post(event.x_root, event.y_root)

    def fill_menu(self):
        """ The the context menu for this node """

        self.menu.add_command(label="Edit", command=lambda: edit_external_file(self.name))
        self.canvas.tag_bind(self.box, "<ButtonPress-2>", self.show_popup)

    def on_click(self, event):
        """ What to do when a visual node is clicked """

        # Allow arborist to see the visualnode
        self.owner.selected_node = self
        self.canvas.update_idletasks()

        if self.visual_parent is None:
            parent = 'None'
        else:
            parent = self.visual_parent.name

        # TODO Flesh this out
        self.visualizer.create_tab(self)

        print '-----------------------------'
        print '| Name:', self.name
        print '| Depth:', self.depth
        print '| Parent:', parent
        print '| Width:', self.width
        print '| # of children:', len(self.children)
        print '| # of visual children:', len(self.visual_children)
        print '| x:', self.x_pos, 'y:', self.y_pos
        print '-----------------------------'


    def on_enter(self, event):
        """ Draw all child links of node """

        pass
        #self.shade_all_children()
        #self.draw_hidden_links()

    def on_leave(self, event):
        """ Do stuff when mouse outta box """

        pass
        #self.unshade_all_children()
        #self.hide_links()

    def set_visual_parent(self):
        """ Set the visual parent to the parent who is depth-- above """

        for parent in self.parents:
            if parent is not None:
                if parent.depth == self.depth - 1:
                    self.visual_parent = parent
        if self.visual_parent is None and self.depth != 1:
            for parent in self.parents:
                print parent.name
            print 'Non-root node without direct parent?'

    def set_visual_children(self):
        """ Return a list of children who are directly below the node """

        for child in self.children:
            if child.visual_parent == self:
                self.visual_children.append(child)

    def set_coordinates(self, offset, modifier=20):
        """ Establish a nodes correct coordinates """

        self.y_pos = self.depth * modifier
        if self.visual_parent:
            self.x_pos = self.visual_parent.x_pos + offset

    def draw(self, size=10):
        """ Call to Tkinter to draw the node on a canvas """

        self.box = self.canvas.create_rectangle(self.x_pos - size, \
                self.y_pos - size, self.x_pos + size, self.y_pos + size, \
                activefill='grey', tags=("all"))
        self.canvas.tag_bind(self.box, '<ButtonPress-1>', self.on_click)
        self.canvas.tag_bind(self.box, "<Enter>", self.on_enter)
        self.canvas.tag_bind(self.box, "<Leave>", self.on_leave)
        self.fill_menu()

    def draw_links(self):
        """ Draw the links linking children to parents """


        for node in self.visual_children:
            if 'definitions' in node.name:
                fill = 'red'
            else:
                fill = 'black'

            self.canvas.create_line(self.x_pos, self.y_pos + 11, \
                    node.x_pos, node.y_pos - 11, arrow='last', fill=fill, tags=("all"))
        self.draw_hidden_links()

    def shade_all_children(self):
        """ Shade all children of node """

        for node in self.children:
            self.canvas.itemconfig(node.box, fill="blue")

    def unshade_all_children(self):
        """ Unshade all children of node """

        for node in self.children:
            self.canvas.itemconfig(node.box, fill="white")

    def draw_hidden_links(self):
        """ Draw links to all children """

        for child in self.children:
            if 'definitions' in child.name:
                fill = 'blue'
            else:
                fill = 'black'

            if child not in self.visual_children:
                self.child_links.append(self.canvas.create_line(self.x_pos, \
                        self.y_pos + 11, child.x_pos, child.y_pos - 11, \
                        arrow='last', fill=fill, tags=("all")))
        self.drawn_hidden = True

    def hide_links(self):
        """ Hide all drawn links to children """

        for child_link in self.child_links:
            self.canvas.delete(child_link)
        self.drawn_hidden = False
