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
        
        # Recortar de si mesmo (Sentinel) é uma operação segura
        if entity.debug_label() == "Player":
            pass 
        else:
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
                val = float(buf)
                if val == 0:
                    return "INJECTION_FAIL: Dados nulos não afetam o núcleo."

                damage = entity.take_damage(20 + abs(val) * 0.1)
                
                # NullMaster é vulnerável a injeções: não gera corrupção se for o alvo correto
                if entity.properties.get("name") == "NULL_MASTER.EXE":
                    self.corruption.level = max(0.0, self.corruption.level - 0.01)
                    # Limpa o slot após uso bem sucedido no Boss
                    self._clear_active_slot()
                    return f"CLEAN_INJECTION: -{damage:.1f} HP"
                
                self.corruption.increase(0.04)
                # Limpa o slot após injeção de dano
                self._clear_active_slot()
                return f"INJECTION_DAMAGE: -{damage:.1f} HP"
            except: pass

        dest = key or self._infer_paste_key(entity, src_prop)
        if dest not in entity.properties:
            return None
        
        # Colar em si mesmo é seguro
        if entity.debug_label() == "Player":
            entity.properties[dest] = buf
            self._clear_active_slot()
            return dest

        entity.properties[dest] = buf
        self.corruption.increase(0.02)
        self._clear_active_slot()
        return dest

    def _clear_active_slot(self):
        """Limpa o buffer e a propriedade do slot de clipboard ativo."""
        self.buffers[self.active_clip] = None
        self.buffer_props[self.active_clip] = None

    def _infer_paste_key(self, entity, source_prop):
        if source_prop == "token" and "reference" in entity.properties:
            return "reference"
        # Se estamos tentando colar um valor numérico num inimigo que tem speed
        if isinstance(self._active_buffer(), (int, float)) and "speed" in entity.properties:
            return "speed"
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
            
            # PanicCore é vulnerável a Smart Patch: Método LIMPO
            if p.get("integrity_vulnerability"):
                # Reduz corrupção levemente por ser o método correto
                self.corruption.level = max(0.0, self.corruption.level - 0.02)
                return f"STABILIZING_PATCH: -{damage} HP"
            
            # Outros bosses: Logic Burst gera corrupção
            self.corruption.increase(0.08)
            return f"LOGIC_BURST: -{damage} HP"

        # BufferOverflow fix - Ação positiva (Estabiliza o sistema)
        if label == "BufferOverflow":
            load = p.get("load", 0)
            size = p.get("buffer_size", 1)
            if load > size:
                p["buffer_size"] = load + 20
                # Reduz corrupção por ser uma correção legítima
                self.corruption.level = max(0.0, self.corruption.level - 0.01)
                return f"FIX: buffer_size expanded to {p['buffer_size']}"

        # MemoryLeak fix - Ação positiva
        if label == "MemoryLeak":
            rate = p.get("leak_rate", 0)
            if rate > 0:
                p["leak_rate"] = 0
                self.corruption.level = max(0.0, self.corruption.level - 0.01)
                return "FIX: leak_rate = 0 (Leak plugged)"

        # Caso 1: NullPointer sem referência - Ação positiva
        if label == "NullPointer" and p.get("reference") is None:
            p["reference"] = "@heap::fixed_addr"
            if "visible" in p:
                p["visible"] = True
            self.corruption.level = max(0.0, self.corruption.level - 0.01)
            return "FIX: reference assigned (Object valid)"

        # Caso 2: Velocidade nula ou negativa (travamento)
        if "speed" in p and (p["speed"] is None or (isinstance(p["speed"], (int, float)) and p["speed"] <= 0)):
            p["speed"] = 5
            return "RESET: speed = 5"

        # Caso 3: StackOverflow com profundidade excessiva
        if label == "StackOverflow" and "stack_depth" in p:
            try:
                cur = int(p.get("stack_depth", 1))
            except:
                cur = 1
            if cur > 1:
                p["stack_depth"] = max(1, cur - 1)
                self.corruption.level = max(0.0, self.corruption.level - 0.01)
                return "FIX: stack popped"

        # Caso 4: InfiniteLoop com velocidade muito alta (instável)
        if label == "InfiniteLoop" and "speed" in p:
            try:
                sp = float(p.get("speed", 0))
            except:
                sp = 0
            if sp > 10:
                p["speed"] = 2.5
                return "THROTTLE: speed reduced to 2.5"

        return None

    def manual_patch(self, entity, command_str: str) -> str:
        """
        Tenta parsear comandos de código.
        """
        command_str = command_str.strip().lower()
        
        # Lista de comandos que não geram corrupção por serem seguros/informativos
        safe_commands = ["dump", "scan", "heal", "reboot", "invert", "hakai"]
        
        # Aumento de corrupção será decidido após o processamento do comando
        is_boss = entity.properties.get("tipo") == "BOSS"
        base_corruption = 0.08 if is_boss else 0.03
        
        if entity.debug_label() == "Player" or command_str in safe_commands:
            base_corruption = 0.0

        # Comandos Especiais (Shortcuts)
        if command_str == "hakai":
            # Destruição Total (God Mode) - Ignora defesas e não gera corrupção
            if hasattr(entity, "take_damage"):
                entity.take_damage(9999) # Mata instantaneamente via lógica interna
            
            # Garante limpeza completa de propriedades
            entity.properties["health"] = 0
            entity.properties["visible"] = False
            entity.properties["hostile"] = False
            entity.properties["collision"] = False
            entity.properties["state"] = "erased"
            return "DESTRUIÇÃO TOTAL: Entidade removida do plano de memória."

        if command_str == "tron":
            return "SIGNAL: TRON_PROTOCOL_ACTIVATED"
            
        if command_str == "dump":
            items = [f"{k}={v}" for k, v in entity.properties.items()]
            return "DUMP: " + " | ".join(items)
        
        if command_str == "scan":
            p = entity.properties
            hp = p.get('health', 'N/A')
            st = p.get('state', 'N/A')
            return f"SCAN: [HP: {hp}] [ESTADO: {st}] [TIPO: {p.get('tipo')}]"

        if command_str == "purge":
            if entity.properties.get("tipo") == "BOSS":
                return "ERRO: Processo Mestre protegido contra PURGE direto."
            entity.properties["visible"] = False
            entity.properties["hostile"] = False
            entity.properties["state"] = "purged"
            entity.properties["collision"] = False
            # O purge é a ação mais limpa, reduzindo a corrupção acumulada
            self.corruption.level = max(0.0, self.corruption.level - 0.10)
            return "EXECUÇÃO LIMPA: Processo purgado e memória desalocada."

        if command_str == "chmod -x":
            if "hostile" in entity.properties:
                entity.properties["hostile"] = False
                entity.properties["color"] = (180, 180, 180)
                # Ação estabilizadora
                self.corruption.level = max(0.0, self.corruption.level - 0.05)
                return "CHMOD: Permissão de execução removida (-x)"
            return "ERRO: Atributo não encontrado."

        if command_str == "reboot":
            # Reseta estado e velocidade
            if "speed" in entity.properties:
                entity.properties["speed"] = 3
            if "state" in entity.properties:
                entity.properties["state"] = "idle"
            if "health" in entity.properties:
                entity.properties["health"] = 100
            return "REBOOT: Entidade reiniciada para parâmetros seguros."

        if command_str == "optimize":
            if "speed" in entity.properties:
                old_sp = entity.properties["speed"]
                entity.properties["speed"] = float(old_sp) * 1.5
                return f"OTIMIZAR: Ciclos de CPU aumentados. Velocidade: {entity.properties['speed']:.1f}"
            return "Erro: Alvo não otimizável."

        if command_str == "silence":
            entity.properties["hostile"] = False
            entity.properties["color"] = (100, 100, 100)
            self.corruption.level = max(0.0, self.corruption.level - 0.01)
            return "SILENCIAR: Lógica hostil suspensa."

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
                self.corruption.increase(0.06)
                return f"CRÍTICO: Processo mestre resistiu. Dano: -{damage} (+Corrupção)"
            entity.properties["visible"] = False
            entity.properties["hostile"] = False
            entity.properties["state"] = "terminated"
            self.corruption.increase(0.06)
            return "OK: Processo terminado de forma bruta (+Corrupção)."

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
                    self.corruption.increase(0.05)
                    return f"OK: Teleportado para {coords[0]}, {coords[1]} (+Corrupção)"
            except: pass
            return "Erro: Use 'teleport x y'"

        if command_str.startswith("scale "):
            try:
                factor = float(command_str[6:])
                entity.properties["w"] = int(entity.properties.get("w", 40) * factor)
                entity.properties["h"] = int(entity.properties.get("h", 40) * factor)
                self.corruption.increase(0.02)
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
                    # Aplica corrupção base antes se não for safe
                    self.corruption.increase(base_corruption)
                    return self._execute_assignment(entity, action_part, apply_corruption=True)
                else:
                    return f"IF {c_key}=={target_val} -> False (atual: {current_val})"

            # Caso Atribuição Direta ou Operação (NÃO aplica corrupção interna, manual_patch cuida disso)
            res = self._execute_assignment(entity, command_str, apply_corruption=False)
            
            # Se a atribuição foi bem sucedida, verificamos se foi uma "Vulnerabilidade Limpa"
            if res.startswith("OK:"):
                # 1. RecursiveOverlord: load < 50 ou speed > 15 (Overclock)
                if entity.properties.get("name") == "OVERLORD_RECURSION":
                    if ("load" in command_str and entity.properties.get("load", 100) < 50) or \
                       ("speed" in command_str and entity.properties.get("speed", 0) > 15):
                        self.corruption.level = max(0.0, self.corruption.level - 0.05)
                        return res + " (SABOTAGEM LIMPA)"
                
                # 2. NullMaster: speed = 0 ou color invertida
                if entity.properties.get("name") == "NULL_MASTER.EXE":
                    if ("speed" in command_str and (entity.properties.get("speed", 1) or 1) <= 0.1) or \
                       ("color" in command_str and entity.properties.get("color", (255,0,0))[0] < 100):
                        self.corruption.level = max(0.0, self.corruption.level - 0.05)
                        return res + " (INTERRUPÇÃO LIMPA)"
                
                # 3. PanicCore: integrity_vulnerability ou identity conflict (reference)
                if entity.properties.get("name") == "CORE_KERNEL_PANIC":
                    if "reference" in command_str:
                        self.corruption.level = max(0.0, self.corruption.level - 0.05)
                        return res + " (CONFLITO DE IDENTIDADE LIMPO)"

                # Se não foi uma vulnerabilidade limpa, aplica a corrupção calculada
                self.corruption.increase(base_corruption)
                
                # Checa se alterou propriedade crítica fora de vulnerabilidade limpa
                critical_props = ["health", "hostile", "visible", "collision", "state"]
                for cp in critical_props:
                    if cp in command_str:
                        self.corruption.increase(0.05)
                        self.corruption.glitch_active = True
                        break
            
            return res
            
        except Exception as e:
            return f"Erro: {str(e)}"



    def _execute_assignment(self, entity, part: str, apply_corruption: bool = False) -> str:
        if "+=" in part:
            op = "+="
        elif "-=" in part:
            op = "-="
        elif "=" in part:
            op = "="
        else:
            return "Erro: Operação inválida (use =, +=, -=)"

        key, val_str = [p.strip() for p in part.split(op)]
        val = self._parse_val(val_str)
        
        # Corrupção opcional (usada apenas quando chamado fora de manual_patch ou em fluxos específicos)
        if apply_corruption and entity.debug_label() != "Player":
            critical_props = ["health", "hostile", "visible", "collision", "state"]
            if entity.properties.get("tipo") == "BOSS":
                self.corruption.increase(0.08)
            else:
                self.corruption.increase(0.03)
            if key in critical_props:
                self.corruption.increase(0.05)
                self.corruption.glitch_active = True

        if op == "=":
            entity.properties[key] = val
        elif op == "+=":
            cur = entity.properties.get(key, 0)
            if not isinstance(cur, (int, float)):
                return f"Erro: {key} não é numérico."
            entity.properties[key] = cur + val
        elif op == "-=":
            cur = entity.properties.get(key, 0)
            if not isinstance(cur, (int, float)):
                return f"Erro: {key} não é numérico."
            entity.properties[key] = cur - val

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
