class Entity:
    def __init__(self):
        self.properties = {}

    def update(self):
        pass

    def render(self, screen):
        pass

    def collide(self, pos):
        x, y = pos
        ex = self.properties.get("x", 0)
        ey = self.properties.get("y", 0)
        w = self.properties.get("w", 40)
        h = self.properties.get("h", 40)

        return ex <= x <= ex + w and ey <= y <= ey + h
