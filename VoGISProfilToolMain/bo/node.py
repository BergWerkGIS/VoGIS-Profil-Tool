class Node:

    def __init__(self, idx):
        self.idx = idx
        self.nxtNd = None
        self.prvNd = None

    def setNext(self, nextNode):
        self.nxtNd = nextNode

    def setPrev(self, prevNode):
        self.prvNd = prevNode

    def toString(self):
        return '{0}\t{1}\t{2}'.format(self.prvNd, self.idx, self.nxtNd)
