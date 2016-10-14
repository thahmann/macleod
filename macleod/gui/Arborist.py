#/usr/bin/python
"""
Class to manage the conversion from a clifModuleSet to a
more generic tree structure

@author Robert Powell
"""

import sys
sys.path.append("../src")

from tkinter import *
from .summary import *
import src.filemgt
import logging
import tkinter.font
import tkinter.ttk

LOG = logging.getLogger(__name__)

# Width of node as counted for tree spacing usually the same as BASE_BUFFER
NODE_BASE_WIDTH = 50
NODE_BASE_HEIGHT = 10
# Minimum space required inside the box
NODE_BASE_BUFFER = 50
TREE_VERTICAL_SPACE = 20
TREE_MAX_WIDTH = 1000
# How many TKinter units to account for each character
CHAR_BASE_WIDTH = False
CHAR_BASE_HEIGHT = False

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
            if src.filemgt.module_is_definition_set(name):
                print(name)
                removes.append(name)

        for name, node in self.nodes.items():
            if 'definition' not in name:
                # TODO refactor these comprehensions
                node.children = [c for c in node.children if not src.filemgt.module_is_definition_set(c.name)]
                node.definitions += [p for p in node.parents if src.filemgt.module_is_definition_set(p.name)]
                node.parents = [p for p in node.parents if not src.filemgt.module_is_definition_set(p.name)]

                for c in node.children:
                    if 'definitions' in c.name:
                        LOG.debug('Did not remove definition in ' + node.name)
                for p in node.parents:
                    if 'definitions' in p.name:
                        LOG.debug('Did not remove definition in ' + node.name)

        visited = self.traverse(self.tree)

        for name, node in self.nodes.items():
            if node not in visited:
                removes.append(name)

        for name in removes:
            try:
                self.nodes.pop(name)
            except KeyError:
                LOG.debug('Already removed definition ' + name)

    def traverse(self, rootnode):
        """ Traverse over the tree marking nodes as reachable """
        visited = [rootnode]
        thislevel = [rootnode]
        while thislevel:
            nextlevel = []
            for n in thislevel:
                visited.append(n)
                if n.children: nextlevel += n.children
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
        self.max_width = TREE_MAX_WIDTH
        self.selected_node = None
        self.get_sizes()


    def gather_nodes(self, clif_set):
        """ Create a dictionary of nodes from a ClifModuleSet """

        self.clif_set = clif_set
        for module in clif_set.imports:
            self.nodes[module.module_name] = VisualNode(module, self.visualizer, self)

    def weight_tree(self):
        """ Climb the tree and weight each level based on its children """

        # Arrange nodes from deepest to root
        nodes = sorted(list(self.nodes.values()), key=lambda n: n.depth, reverse=True)

        # First make sure all nodes width is that of their definition 
        for node in nodes:
            node.set_visual_parent()
            node.set_visual_children()
            node.set_height()
            node.set_width()

        for node in nodes:
            if len(node.visual_children) == 0:
                # Edge case for many no-children siblings
                node.width += 15
            if len(node.visual_children) == 1:
                node.width = max(node.visual_children[0].width, node.width)
            else:
                node.width = max(sum(c.width for c in node.visual_children), node.width)


    # TODO Don't know if this belongs here
    def remove_tree(self):
        """ Remove the drawn elements of the tree from canvas """

        self.canvas.delete(ALL)

    def layout_tree(self):
        """ Layout the tree by setting the coordinates for each node """

        self.tree.x_pos = 0.5 * self.max_width
        self.tree.y_pos = TREE_VERTICAL_SPACE

        levels = {}
        for node in sorted(list(self.nodes.values()), key=lambda n: n.depth):
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
                        node.x_pos = node.visual_parent.x_pos \
                                - (0.5 * node.visual_parent.width) \
                                + node.visual_parent.offset \
                                + 0.5 * node.width

                    node.visual_parent.offset += node.width
                    node.y_pos = node.visual_parent.y_pos + \
                                node.visual_parent.height + node.height + 20

    def draw_tree(self):
        """ Use Tkinter to draw the nodes on canvas """

        [node.draw() for node in list(self.nodes.values())]
        [node.draw_links() for node in list(self.nodes.values())]

    def get_sizes(self):
        """ Get the pixel width/height of text on screen """

        global CHAR_BASE_HEIGHT, CHAR_BASE_WIDTH

        temp = Canvas()
        text = temp.create_text((0, 0), text='abcdefghijklmnopqrstuvwxyz_')
        size = temp.bbox(text)
        CHAR_BASE_WIDTH = size[2] / 10 / 2
        CHAR_BASE_HEIGHT = size[3] * 2

    def adjust_text(self, size):
        """ Either increase or decrease font size for all nodes """

        for node in list(self.nodes.values()):
            if size:
                node.font_size += 1
            else:
                node.font_size -= 1

            self.canvas.itemconfig(node.canvas_text, font=('Purisa', node.font_size))


class Node(object):
    """ Generic node object for the tree """

    def __init__(self, clif_module):
        """ Create a new node from a ClifModule """

        self.name = clif_module.module_name
        self.parents = []
        self.children = []
        self.definitions = []
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
        self.canvas_text = None
        self.font_size = 13
        self.box = None
        self.x_pos = 0
        self.y_pos = 0
        self.height = NODE_BASE_HEIGHT
        self.r_width = 0 #NODE_BASE_BUFFER
        self.visual_parent = None
        self.visual_children = []
        self.width = 0
        self.offset = 0
        self.information = {}
        self.child_links = []
        self.parent_links = []
        self.drawn_hidden = False
        self.owner = owner

    def set_height(self):
        """ Set the height of the node relative to definitions """

        if len(self.definitions) > 0:
            self.height = len(self.definitions) * CHAR_BASE_HEIGHT
        else:
            self.height = 15

    def set_width(self):
        """ Set the width relative to maximum definition name """

        def_width = 0
        name_width = len(self.name) * CHAR_BASE_WIDTH
        if len(self.definitions) != 0:
            def_width = len(max([c.name for c in self.definitions], key=len)) * CHAR_BASE_WIDTH

        self.width = max(def_width, name_width)
        self.r_width = self.width 

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

        self.visualizer.create_tab(self)

        print('-----------------------------')
        print('| Name:', self.name)
        print('| Depth:', self.depth)
        print('| Parent:', parent)
        print('| Width:', self.width)
        print('| # of children:', len(self.children))
        print('| # of visual children:', len(self.visual_children))
        print('| x:', self.x_pos, 'y:', self.y_pos)
        print('-----------------------------')

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
                print(parent.name)
            LOG.debug('Non-root node without parent ' + self.name)

    def set_visual_children(self):
        """ Return a list of children who are directly below the node """

        for child in self.children:
            if child.visual_parent == self:
                self.visual_children.append(child)

    def draw(self):
        """ Call to Tkinter to draw the node on a canvas """

        self.box = self.canvas.create_rectangle(self.x_pos - self.r_width / 2, \
                self.y_pos - self.height, self.x_pos + self.r_width / 2, \
                self.y_pos + self.height / 2., activefill='grey', tags=("all"))
        self.canvas.tag_bind(self.box, '<ButtonPress-1>', self.on_click)
        self.canvas.tag_bind(self.box, "<Enter>", self.on_enter)
        self.canvas.tag_bind(self.box, "<Leave>", self.on_leave)
        self.fill_menu()
        self.fill_box()

    def fill_box(self):
        """ Fill in description text in node """

        # The minus CHAR_BASE_HEIGHT is to get the first line (name) outside the box
        self.canvas_text = self.canvas.create_text(self.x_pos - self.r_width / 2, \
                self.y_pos - self.height - CHAR_BASE_HEIGHT, anchor="nw")
        text_string = self.name.split('/')[-1] + '\n'
        text_string += "\n".join([n.name.split('/')[-1] for n in self.definitions])
        self.canvas.itemconfig(self.canvas_text, font=('Purisa', self.font_size), text=text_string)

    def draw_links(self):
        """ Draw the links linking children to parents """

        for node in self.visual_children:
            if 'definitions' in node.name:
                fill = 'red'
            else:
                fill = 'black'

            self.canvas.create_line(self.x_pos, self.y_pos + self.height / 2, \
                    node.x_pos, node.y_pos - node.height - 5, arrow='last', \
                    fill=fill, tags=("all"))
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
                        self.y_pos + self.height / 2, child.x_pos, child.y_pos - \
                        child.height - 5, arrow='last', fill=fill, tags=("all")))
        self.drawn_hidden = True

    def hide_links(self):
        """ Hide all drawn links to children """

        for child_link in self.child_links:
            self.canvas.delete(child_link)
        self.drawn_hidden = False
