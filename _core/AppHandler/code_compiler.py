opcode_map = {
    'NOP': '0x00',
    'LOAD': '0x01',
    'STORE': '0x02',
    'ADD': '0x03',
    'JUMP': '0x04',
    'PRINT': '0x05',
    'HALT': '0x06',
    'SUB': '0x07',
    'MULT': '0x08',
    'DIV': '0x09',
    'MOD': '0x0A',
    'AND': '0x0B',
    'OR': '0x0C',
    'XOR': '0x0D',
    'NOT': '0x0E',
    'EXEC': '0x0F',
    'EXPY': '0x10',
    'RETURN': '0x11'
}

reversed_opcode_map = {v: k for k, v in opcode_map.items()}


def ishex(string: str) -> bool:
    try:
        int(string, 16)
        return True
    except ValueError:
        return False


class Compile:
    def __init__(self, asm: str):
        lines = asm.strip().split("\n")
        self.labels = {}
        label_less = []
        self.compiled_code = ["!8-bit-code", ""]

        # First pass: collect labels and clean up lines
        current_address = 0
        for line in lines:
            line = line.strip()
            if not line or line.startswith(";"):
                continue
            if line.endswith(":"):
                label_name = line.replace(":", "").strip()
                self.labels[label_name] = current_address
            else:
                label_less.append(line)
                current_address += 1

        # Second pass: compile
        for line in label_less:
            tokens = line.strip().split()
            cmd = tokens[0].upper()
            args = tokens[1:]

            if cmd not in opcode_map:
                raise SyntaxError(f"Unknown instruction: {cmd}")

            if cmd == "JUMP":
                label = args[0]
                if label not in self.labels:
                    if ishex(label):
                        self.compiled_code.append(f"{opcode_map[cmd]} 0x{int(label, 16):02X}")
                        continue
                    raise ValueError(f"Unknown label: {label}")
                addr = self.labels[label] + 1  # Add one because the first line starts at 1
                self.compiled_code.append(f"{opcode_map[cmd]} 0x{addr:02X}")
            else:
                self.compiled_code.append(f"{opcode_map[cmd]} {' '.join(args)}")

    def get_output(self):
        return "\n".join(self.compiled_code)


def main() -> None:
    code = Compile(r"""
    start:
        JUMP 0x01
    """).get_output()
    print(code)

if __name__ == "__main__":
    main()
