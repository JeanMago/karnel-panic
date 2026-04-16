class DebuggerGun:
    """
    Dois slots de clipboard (A e B) para permitir trocas (ex.: duas velocidades).
    CUT e PASTE usam sempre o slot **ativo** ([TAB] alterna).
    """

    def __init__(self, corruption):
        self.buffers = [None, None]
        self.buffer_props = [None, None]
        self.active_clip = 0
        self.corruption = corruption

    def cycle_clip(self) -> int:
        self.active_clip = 1 - self.active_clip
        return self.active_clip

    def _active_buffer(self):
        return self.buffers[self.active_clip]

    def _active_prop(self):
        return self.buffer_props[self.active_clip]

    def buffer_status_lines(self):
        rows = []
        for i in range(2):
            mark = "►" if i == self.active_clip else " "
            name = "A" if i == 0 else "B"
            b, p = self.buffers[i], self.buffer_props[i]
            if b is None:
                rows.append(f"{mark} slot {name}: (vazio)")
            else:
                val = repr(b)
                if len(val) > 34:
                    val = val[:31] + "..."
                rows.append(f"{mark} slot {name} [{p}]: {val}")
        rows.append("[TAB] troca slot ativo  |  [X]=CUT  [V]=PASTE usam o slot ►")
        return rows

    def peek_cut_key(self, entity) -> str | None:
        if "speed" in entity.properties:
            return "speed"
        if entity.debug_label() == "Player" and "token" in entity.properties:
            return "token"
        if "stack_depth" in entity.properties:
            return "stack_depth"
        return None

    def peek_paste_destination(self, entity) -> str | None:
        if self._active_buffer() is None:
            return None
        dest = self._infer_paste_key(entity, self._active_prop())
        if dest in entity.properties:
            return dest
        return None

    def inspect(self, entity):
        return dict(entity.properties)

    def cut(self, entity, key):
        if key not in entity.properties:
            return False
        if entity.properties.get(key) is None:
            return False
        i = self.active_clip
        self.buffers[i] = entity.properties[key]
        self.buffer_props[i] = key
        entity.properties[key] = None
        self.corruption.increase(0.05)
        return True

    def paste(self, entity, key=None):
        buf = self._active_buffer()
        src_prop = self._active_prop()
        if buf is None:
            return None
        dest = key or self._infer_paste_key(entity, src_prop)
        if dest not in entity.properties:
            return None
        entity.properties[dest] = buf
        self.corruption.increase(0.05)
        return dest

    def _infer_paste_key(self, entity, source_prop):
        if source_prop == "token" and "reference" in entity.properties:
            return "reference"
        return source_prop or "speed"

    def patch(self, entity, key, condition, new_value):
        cur = entity.properties.get(key)
        if not condition(cur):
            return False
        entity.properties[key] = new_value
        self.corruption.increase(0.1)
        return True

    def smart_patch(self, entity):
        p = entity.properties

        if "reference" in p and p.get("reference") is None:
            p["reference"] = "@heap::valid#1"
            if "visible" in p:
                p["visible"] = True
            if p.get("speed") is None or p.get("speed") == 0:
                p["speed"] = 20
            self.corruption.increase(0.08)
            return "reference"

        if self.patch(
            entity,
            "speed",
            lambda v: v is None or (isinstance(v, (int, float)) and v < 1),
            5,
        ):
            return "speed"

        if "stack_depth" in p:
            try:
                cur = int(p.get("stack_depth", 1))
            except (TypeError, ValueError):
                cur = 1
            if cur > 1 and self.patch(
                entity, "stack_depth", lambda v: True, max(1, cur - 2)
            ):
                return "stack_depth"

        return None
