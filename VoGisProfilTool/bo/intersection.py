class Intersection:

    def __init__(self, from_x, from_y, from_z, from_dist, to_x, to_y, to_z, to_dist):

        self.from_x = from_x
        self.from_y = from_y
        self.from_z = from_z
        self.from_dist = from_dist
        self.to_x = to_x
        self.to_y = to_y
        self.to_z = to_z
        self.to_dist = to_dist


    def toStr(self):
        return '{0}/{1} z:{2} dist:{3} -> {4}/{5} z:{6} dist:{7}'.format(
                          self.from_x,
                          self.from_y,
                          self.from_z,
                          self.from_dist,
                          self.to_x,
                          self.to_y,
                          self.to_z,
                          self.to_dist
                          )
