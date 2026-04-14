class GameLoop:
    def __init__(self):
        self.entities = []

    def add_entity(self, e):
        self.entities.append(e)

    def update(self):
        for e in self.entities:
            e.update()

    def render(self, screen):
        for e in self.entities:
            e.render(screen)
