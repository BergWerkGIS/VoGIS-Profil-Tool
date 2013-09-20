class Settings:

    def __init__(
        self,
        mapData
    ):

        self.mapData = mapData
        self.modeLine = enumModeLine.line
        self.modeVertices = enumModeVertices.equiDistant
        self.onlyHektoMode = False
        self.onlySelectedFeatures = False
        self.linesExplode = True
        self.linesMerge = True
        self.equiDistance = 10.0
        self.vertexCnt = 100
        self.createHekto = False
        self.nodesAndVertices = False


class enumVertexType:
    #start oder endpunkt
    node = 0
    #vertex aus geometrie
    vertex = 1
    #errechneter profil punkt
    point = 2


class enumModeLine:
    customLine = 0
    line = 1
    straightLine = 2


class enumModeVertices:
    equiDistant = 0
    vertexCnt = 1
