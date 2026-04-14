class DebuggerGun:
    def __init__(self, corruption):
        self.buffer = None
        self.corruption = corruption

    def inspect(self, entity):
        return entity.properties

    def cut(self, entity, key):
        if key in entity.properties:
            self.buffer = entity.properties[key]
            entity.properties[key] = None
            self.corruption.increase(0.05)

    def paste(self, entity, key):
        if self.buffer is not None:
            entity.properties[key] = self.buffer
            self.corruption.increase(0.05)

    def patch(self, entity, key, condition, new_value):
        if condition(entity.properties.get(key)):
            entity.properties[key] = new_value
            self.corruption.increase(0.1)
