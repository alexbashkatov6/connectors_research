from anytree import Node, RenderTree, PreOrderIter
from anytree.exporter import DotExporter
import graphviz


class A:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.name)


# udo = Node("Udo")
# marc = Node("Marc", parent=udo)
# lian = Node("Lian", parent=marc)
# dan = Node("Dan", parent=udo)
# jet = Node("Jet", parent=dan)
# jan = Node("Jan", parent=dan)
# joe = Node("Joe", parent=dan)
#
# print(udo)
# print(joe)
# for pre, fill, node in RenderTree(udo):
#     print("%s%s" % (pre, node.name))
# print(dan.children)
# print([node.name for node in PreOrderIter(udo)])

udo = Node(A("Udo"))
marc = Node(A("Marc"), parent=udo)
lian = Node(A("Lian"), parent=marc)
dan = Node(A("Dan"), parent=udo)
jet = Node(A("Jet"), parent=dan)
jan = Node(A("Jan"), parent=dan)
joe = Node(A("Joe"), parent=dan)

print(udo)
print(joe)
for pre, fill, node in RenderTree(udo):
    print("%s%s" % (pre, node.name))
print(dan.children)

# DotExporter(udo).to_picture("udo.png")
print([node.name for node in PreOrderIter(udo)])
