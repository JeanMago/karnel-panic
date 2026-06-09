class Entity:
    """Base leve: estado editável em `properties`; comportamento em subclasses."""

    def __init__(self):
        self.properties = {}

    def debug_label(self) -> str:
        return self.__class__.__name__

    def update(self, dt):
        """Atualização lógica (opcional em subclasses)."""
        pass

    def render(self, screen):
        """Desenho da entidade (opcional em subclasses)."""
        pass

    def is_hostile(self) -> bool:
        return bool(self.properties.get("hostile"))

    def should_render(self) -> bool:
        """Verifica se a entidade deve ser desenhada."""
        return bool(self.properties.get("visible", True))

    def collide(self, pos):
        # Se a colisão estiver desativada ou a vida for zero, ignora
        if not self.properties.get("collision", True):
            return False
        if self.properties.get("health", 1) is not None and self.properties.get("health", 1) <= 0:
            return False

        x, y = pos
        ex = self.properties.get("x", 0)
        ey = self.properties.get("y", 0)
        w = self.properties.get("w", 40)
        h = self.properties.get("h", 40)

        return ex <= x <= ex + w and ey <= y <= ey + h
