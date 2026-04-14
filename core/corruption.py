class CorruptionSystem:
    def __init__(self):
        self.level = 0.0

    def increase(self, amount):
        self.level = min(1.0, self.level + amount)

    def get_color_shift(self):
        return int(self.level * 120)
