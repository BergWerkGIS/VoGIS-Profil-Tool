class Line:
    def __init__(self, id, name, line):
        self.id = id
        self.name = name
        self.line = line
        self.selected = False

    def toStr(self):
        return self.id + ": " + self.name
