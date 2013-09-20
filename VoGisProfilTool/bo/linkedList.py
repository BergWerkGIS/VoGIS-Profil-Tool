#from node import Node


class LinkedList:

    def __init__(self):
        self.nodes = []

    def addNode(self, n):
        self.nodes.append(n)

    def getOrderedIds(self):

        ordered = []
        #alleinstehende Nodes
        for i, n in enumerate(self.nodes):
            if n.prvNd is None and n.nxtNd is None:
                ordered.append(n.idx)

        #start indices
        for i, n in enumerate(self.nodes):
            if n.prvNd is None and n.nxtNd is not None:
                ordered = self.__iterList(i, ordered)

        return ordered

    def __iterList(self, idx, ordered):
        ordered.append(idx)
        if self.nodes[idx].nxtNd is not None:
            ordered = self.__iterList(self.nodes[idx].nxtNd, ordered)
        return ordered
