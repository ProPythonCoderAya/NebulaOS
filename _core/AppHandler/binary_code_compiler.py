import os
from _core.AppHandler import opcode_map, reversed_opcode_map, Compile, AppReader, AppRunner
from _core import Disk
import datetime


class BinaryCompile:
    class VersionError(Exception): pass

    def __init__(self, asm: str):
        self.instructions: list[str] = Compile(asm).get_raw()[2:]
        self.compiled_binary = b""
        self.total_instructions = 0
        for instr in self.instructions:
            instr = instr.strip().split()
            cmd = instr[0]
            args = instr[1:]
            self.compiled_binary += chr(int(cmd, 16)).encode("utf-8")
            self.compiled_binary += len(args).to_bytes(1, "big")
            self.total_instructions += 1

            for arg in args:
                self.compiled_binary += arg.encode("utf-8")
                self.compiled_binary += b"\x00"

    def to_bytes(self):
        return b"NSB" + (1).to_bytes(2, "big") + self.total_instructions.to_bytes(2, "big") + self.compiled_binary

    def save(self, path):
        with open(path, "wb") as f:
            f.write(self.to_bytes())

    @staticmethod
    def load(path: str, readable_by_AppReader=False, human_readable=False) -> str:
        with open(path, "rb") as f:
            if f.read(3) != b"NSB":
                raise TypeError("Not a NStar Binary!")
            version = int.from_bytes(f.read(2), "big")
            if version != 1:
                raise BinaryCompile.VersionError(f"Unknown version: {version}")
            instruction_count = int.from_bytes(f.read(2), "big")
            binary = f.read()

        output_lines = []
        if readable_by_AppReader:
            output_lines = ["!8-bit-code", ""]
        if human_readable and readable_by_AppReader:
            raise SyntaxError("Cannot be human and AppReader readable at the same time.")
        i = 0
        while i < len(binary):
            opcode = f"0x{binary[i]:02X}"
            if human_readable:
                opcode = reversed_opcode_map.get(opcode)
            i += 1
            arg_length = binary[i]
            i += 1

            args = []
            for _ in range(arg_length):
                arg = b""
                while i < len(binary) and binary[i] != 0x00:
                    arg += bytes([binary[i]])
                    i += 1
                i += 1  # Skip null terminator
                args.append(arg.decode("utf-8"))

            output_lines.append(f"{opcode} {' '.join(args)}")

        return "\n".join(output_lines)

    def __repr__(self):
        return "Cannot print as string."


def main() -> None:
    binary = BinaryCompile(r"""
    start:
        LOAD r0 0x41
        PRINT -A \r0
        HALT
    """)
    binary.save("example.nsb")

    # Later...
    code = BinaryCompile.load("example.nsb", readable_by_AppReader=True)
    Disk.load()
    app = AppRunner(code, "/")
    current_time = datetime.datetime.now()
    logfile = f"{current_time.strftime('%Y-%m-%d--%H:%M:%S')}.log"
    os.system(f"mkdir -p ~/.nebulaos ; touch ~/.nebulaos/{logfile}")
    with open(f"/Users/VICKY/.nebulaos/{logfile}", "w") as log:
        app.run(log_file=log)

if __name__ == "__main__":
    main()
