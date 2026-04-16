class Entity:
    """Base leve: estado editável em `properties`; comportamento em subclasses."""

    def __init__(self):
        self.properties = {}

    def debug_label(self) -> str:
        return self.__class__.__name__

    def is_hostile(self) -> bool:
        return bool(self.properties.get("hostile"))

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
