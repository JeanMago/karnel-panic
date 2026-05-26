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
        p = entity.properties
        if "speed" in p: return "speed"
        if entity.debug_label() == "Player" and "token" in p: return "token"
        if "stack_depth" in p: return "stack_depth"
        if "load" in p: return "load"
        if "leak_rate" in p: return "leak_rate"
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
        self.corruption.increase(0.02)
        return True

    def paste(self, entity, key=None):
        buf = self._active_buffer()
        src_prop = self._active_prop()
        if buf is None:
            return None
            
        # Injeção de Dano em BOSS
        if entity.properties.get("tipo") == "BOSS":
            try:
                # Se colarmos um valor numérico em qualquer lugar do Boss, causa dano
                val = float(buf)
                damage = entity.take_damage(20 + abs(val) * 0.1)
                self.corruption.increase(0.04)
                return f"INJECTION_DAMAGE: -{damage:.1f} HP"
            except: pass

        dest = key or self._infer_paste_key(entity, src_prop)
        if dest not in entity.properties:
            return None
        entity.properties[dest] = buf
        self.corruption.increase(0.02)
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
        self.corruption.increase(0.05)
        return True

    def smart_patch(self, entity):
        p = entity.properties
        label = entity.debug_label()

        # Dano direto em BOSS via Smart Patch (Logic Burst)
        if p.get("tipo") == "BOSS":
            damage = entity.take_damage(50)
            self.corruption.increase(0.08)
            return f"LOGIC_BURST: -{damage} HP"

        # BufferOverflow fix
        if label == "BufferOverflow":
            load = p.get("load", 0)
            size = p.get("buffer_size", 1)
            if load > size:
                p["buffer_size"] = load + 20
                self.corruption.increase(0.03)
                return f"ALLOC: buffer_size = {p['buffer_size']}"

        # MemoryLeak fix
        if label == "MemoryLeak":
            rate = p.get("leak_rate", 0)
            if rate > 0:
                p["leak_rate"] = 0
                self.corruption.increase(0.02)
                return "PATCH: leak_rate = 0 (Memory fixed)"

        # Caso 1: NullPointer sem referência
        if label == "NullPointer" and p.get("reference") is None:
            p["reference"] = "@heap::fixed_addr"
            if "visible" in p:
                p["visible"] = True
            self.corruption.increase(0.04)
            return "IF (ref == NULL) -> ref = @heap::fixed"

        # Caso 2: Velocidade nula ou negativa (travamento)
        if "speed" in p and (p["speed"] is None or (isinstance(p["speed"], (int, float)) and p["speed"] <= 0)):
            p["speed"] = 5
            self.corruption.increase(0.02)
            return "IF (speed <= 0) -> speed = 5"

        # Caso 3: StackOverflow com profundidade excessiva
        if label == "StackOverflow" and "stack_depth" in p:
            try:
                cur = int(p.get("stack_depth", 1))
            except:
                cur = 1
            if cur > 1:
                p["stack_depth"] = max(1, cur - 1)
                self.corruption.increase(0.03)
                return "WHILE (stack > 1) -> stack--"

        # Caso 4: InfiniteLoop com velocidade muito alta (instável)
        if label == "InfiniteLoop" and "speed" in p:
            try:
                sp = float(p.get("speed", 0))
            except:
                sp = 0
            if sp > 10:
                p["speed"] = 2.5
                self.corruption.increase(0.02)
                return "IF (speed > 10) -> speed = 2.5 (throttle)"

        return None

    def manual_patch(self, entity, command_str: str) -> str:
        """
        Tenta parsear comandos de código.
        """
        command_str = command_str.strip().lower()
        self.corruption.increase(0.05)

        # Comandos Especiais (Shortcuts)
        if command_str == "dump":
            items = [f"{k}={v}" for k, v in entity.properties.items()]
            return "DUMP: " + " | ".join(items)
        
        if command_str == "freeze":
            if "speed" in entity.properties:
                entity.properties["speed"] = 0
                return "OK: speed = 0 (Congelado)"
            return "Erro: Alvo não possui propriedade 'speed'"

        if command_str == "unfreeze":
            if "speed" in entity.properties:
                entity.properties["speed"] = 5
                return "OK: speed = 5 (Descongelado)"
            return "Erro: Alvo não possui propriedade 'speed'"

        if command_str == "kill":
            if entity.properties.get("tipo") == "BOSS":
                damage = entity.take_damage(100)
                return f"CRITICAL: Processo mestre resistiu. Dano: -{damage}"
            entity.properties["visible"] = False
            entity.properties["hostile"] = False
            entity.properties["state"] = "terminated"
            return "OK: Processo terminado."

        if command_str == "heal":
            if "health" in entity.properties:
                entity.properties["health"] = 100
                return "OK: Integridade restaurada (100%)"
            return "Erro: Alvo não possui propriedade 'health'"

        if command_str == "invert":
            if "color" in entity.properties:
                c = entity.properties["color"]
                entity.properties["color"] = (255 - c[0], 255 - c[1], 255 - c[2])
                return f"OK: Cores invertidas para {entity.properties['color']}"
            return "Erro: Alvo não possui propriedade 'color'"

        if command_str.startswith("teleport "):
            try:
                coords = command_str[9:].replace(",", " ").split()
                if len(coords) == 2:
                    entity.properties["x"] = float(coords[0])
                    entity.properties["y"] = float(coords[1])
                    return f"OK: Teleportado para {coords[0]}, {coords[1]}"
            except: pass
            return "Erro: Use 'teleport x y'"

        if command_str.startswith("scale "):
            try:
                factor = float(command_str[6:])
                entity.properties["w"] = int(entity.properties.get("w", 40) * factor)
                entity.properties["h"] = int(entity.properties.get("h", 40) * factor)
                return f"OK: Escalonado por {factor}"
            except: pass
            return "Erro: Use 'scale fator'"

        try:
            # Caso IF: if prop == val: prop2 = val2
            if command_str.startswith("if "):
                parts = command_str[3:].split(":")
                if len(parts) != 2:
                    return "Erro: Formato IF incorreto. Use 'if p == v: p2 = v2'"
                
                cond_part = parts[0].strip()
                action_part = parts[1].strip()

                if "==" not in cond_part:
                    return "Erro: Apenas '==' suportado no IF."
                
                c_key, c_val = [p.strip() for p in cond_part.split("==")]
                if c_key not in entity.properties:
                    return f"Erro: {c_key} não existe."
                
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
        
        if (val_str.startswith("'") and val_str.endswith("'")) or \
           (val_str.startswith('"') and val_str.endswith('"')):
            return val_str[1:-1]
            
        return val_str
