class GameLoop:
    def __init__(self):
        self.entities = []

    def add_entity(self, e):
        self.entities.append(e)

    def update(self, dt):
        for e in self.entities:
            e.update(dt)

    def render(self, screen):
        for e in self.entities:
            e.render(screen)
