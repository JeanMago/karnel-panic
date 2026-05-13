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
        label = entity.debug_label()

        # Caso 1: NullPointer sem referência
        if label == "NullPointer" and p.get("reference") is None:
            # Simulando: if (ref == null) ref = @heap_alloc()
            p["reference"] = "@heap::fixed_addr"
            if "visible" in p:
                p["visible"] = True
            self.corruption.increase(0.08)
            return "IF (ref == NULL) -> ref = @heap::fixed"

        # Caso 2: Velocidade nula ou negativa (travamento)
        if "speed" in p and (p["speed"] is None or (isinstance(p["speed"], (int, float)) and p["speed"] <= 0)):
            # Simulando: if (speed <= 0) speed = DEFAULT_SPEED
            p["speed"] = 5
            self.corruption.increase(0.05)
            return "IF (speed <= 0) -> speed = 5"

        # Caso 3: StackOverflow com profundidade excessiva
        if label == "StackOverflow" and "stack_depth" in p:
            try:
                cur = int(p.get("stack_depth", 1))
            except (TypeError, ValueError):
                cur = 1
            if cur > 1:
                # Simulando: while (depth > 1) depth--
                p["stack_depth"] = max(1, cur - 1)
                self.corruption.increase(0.06)
                return "WHILE (stack > 1) -> stack--"

        # Caso 4: InfiniteLoop com velocidade muito alta (instável)
        if label == "InfiniteLoop" and "speed" in p:
            try:
                sp = float(p.get("speed", 0))
            except (TypeError, ValueError):
                sp = 0
            if sp > 10:
                p["speed"] = 2.5
                self.corruption.increase(0.04)
                return "IF (speed > 10) -> speed = 2.5 (throttle)"

        return None

    def manual_patch(self, entity, command_str: str) -> str:
        """
        Tenta parsear comandos de código.
        Formatos suportados:
        - prop = valor
        - prop += valor
        - prop -= valor
        - if prop == valor: prop2 = valor2
        """
        command_str = command_str.strip()
        self.corruption.increase(0.1)

        try:
            # Caso IF: if prop == val: prop2 = val2
            if command_str.startswith("if "):
                parts = command_str[3:].split(":")
                if len(parts) != 2:
                    return "Erro: Formato IF incorreto. Use 'if p == v: p2 = v2'"
                
                cond_part = parts[0].strip()
                action_part = parts[1].strip()

                # Simplificação: apenas == suportado por enquanto
                if "==" not in cond_part:
                    return "Erro: Apenas '==' suportado no IF."
                
                c_key, c_val = [p.strip() for p in cond_part.split("==")]
                if c_key not in entity.properties:
                    return f"Erro: {c_key} não existe."
                
                # Checa condição
                current_val = entity.properties[c_key]
                target_val = self._parse_val(c_val)

                if current_val == target_val:
                    return self._execute_assignment(entity, action_part)
                else:
                    return f"IF {c_key}=={target_val} -> False (atual: {current_val})"

            # Caso Atribuição Direta ou Operação
            return self._execute_assignment(entity, command_str)
            
        except Exception as e:
            return f"Erro: {str(e)}"

    def _execute_assignment(self, entity, part: str) -> str:
        if "+=" in part:
            op = "+="
        elif "-=" in part:
            op = "-="
        elif "=" in part:
            op = "="
        else:
            return "Erro: Operação inválida (use =, +=, -=)"

        key, val_str = [p.strip() for p in part.split(op)]
        if key not in entity.properties:
            return f"Erro: {key} não existe."

        val = self._parse_val(val_str)
        
        if op == "=":
            entity.properties[key] = val
        elif op == "+=":
            if not isinstance(entity.properties[key], (int, float)):
                return f"Erro: {key} não é numérico."
            entity.properties[key] += val
        elif op == "-=":
            if not isinstance(entity.properties[key], (int, float)):
                return f"Erro: {key} não é numérico."
            entity.properties[key] -= val

        return f"OK: {key} {op} {val}"

    def _parse_val(self, val_str: str):
        val_str = val_str.strip()
        if val_str.isdigit():
            return int(val_str)
        try:
            return float(val_str)
        except ValueError:
            pass
        
        if val_str.lower() == "true": return True
        if val_str.lower() == "false": return False
        if val_str.lower() == "none" or val_str.lower() == "null": return None
        
        # Remove aspas se houver
        if (val_str.startswith("'") and val_str.endswith("'")) or \
           (val_str.startswith('"') and val_str.endswith('"')):
            return val_str[1:-1]
            
        return val_str
