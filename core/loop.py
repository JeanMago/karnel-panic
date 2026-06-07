class GameLoop:
    def __init__(self):
        self.entities = []

    def add_entity(self, e):
        self.entities.append(e)

    def update(self, dt):
        for e in self.entities:
            # Pula update de entidades "mortas" ou invisíveis por sistema
            if e.properties.get("health", 1) is not None and e.properties.get("health", 1) <= 0:
                continue
            e.update(dt)

    def render(self, screen):
        for e in self.entities:
            if hasattr(e, "should_render") and not e.should_render():
                continue
            e.render(screen)
