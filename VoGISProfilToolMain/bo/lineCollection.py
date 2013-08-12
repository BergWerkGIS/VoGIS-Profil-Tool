class LineCollection(object):
    """docstring for LineCollection"""
    def __init__(self):
        self.__lines = []

    def addLine(self, line):
        self.__lines.append(line)

    def getById(self, id):
        if len(self.__lines) < 1:
            return None
        for r in self.__lines:
            if r.id == id:
                return r

    def count(self):
        return len(self.__lines)

    def lines(self):
        return self.__lines
