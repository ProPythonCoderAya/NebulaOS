import json
import os
import io
import sys
import pygame
from typing import Literal
from _core import Disk, GlobalUtils
from _core.AppHandler import GUI


class AppRunner:
    class NeapExecutionError(Exception): pass
    class InvalidInstructionError(NeapExecutionError): pass

    def __init__(self, code, cwd, mode: Literal['safe', 'debug', 'normal'] = 'safe') -> None:
        self.mode = mode
        self.cwd = cwd
        self.code = code
        self.regs = {}
        for i in range(10):
            self.regs['r' + str(i)] = 0  # Initialize registers r0-r9
        self.mem = {}
        for i in range(255):
            self.mem[f"0x{i:02X}"] = 0  # Initialize memory with 255 locations

    def run(self, log_file=sys.stderr):
        code = self.code.strip().split('\n')

        if code[0] != '!8-bit-code':
            raise TypeError("Unsupported format: {0}".format(code[0][1:]))
        code = code[1:]
        pc = 0
        curr_iter = 0
        max_iter = 1000
        while pc < len(code):
            if curr_iter > max_iter and self.mode == 'safe':
                raise RecursionError(f'Max recursion reached. Please do not use recursive functions without end in safe mode.')
            line = code[pc]
            cmd: list[str] = line.split()
            if not cmd:
                pc += 1
                continue
            if cmd[0] in ';!':  # Semicolons for comments
                pc += 1
                continue
            elif cmd[0] == '0x00':
                pc += 1
                continue  # No operation (NOP)
            elif cmd[0] == '0x01':  # LOAD
                if len(cmd) < 3:
                    raise TypeError("LOAD not given enough arguments")
                self.regs[cmd[1]] = int(cmd[2], 16)
            elif cmd[0] == '0x02':  # STORE
                if len(cmd) < 3:
                    raise TypeError("STORE not given enough arguments")
                self.mem[cmd[2]] = self.regs[cmd[1]]
            elif cmd[0] == '0x03':  # ADD
                if len(cmd) < 4:
                    raise TypeError("ADD not given enough arguments")
                self.regs[cmd[3]] = self.regs[cmd[1]] + self.regs[cmd[2]]
            elif cmd[0] == '0x04':  # JUMP
                if len(cmd) < 2:
                    raise TypeError("JUMP not given enough arguments")
                curr_iter += 1
                pc = int(cmd[1], 16) - 1  # Jump to address
                continue  # We need to call continue or well go to the wrong address
            elif cmd[0] == '0x05':  # PRINT with dynamic register replacement and colors
                if len(cmd) < 2:
                    raise TypeError("PRINT not given enough arguments")

                message = ''
                print_ascii = cmd[1] == "-A"
                if print_ascii:
                    cmd = cmd[1:]
                for word in cmd[1:]:
                    if word == ';':
                        break
                    message += word + ' '
                message = message.strip()

                # Replace register placeholders (\rX) with their values
                for reg in self.regs.keys():
                    message = message.replace(f"\\{reg}", str(self.regs[reg]))

                new_message = message.split()
                message = ""
                for word in new_message:
                    if print_ascii and word.isnumeric():
                        word = chr(int(word))
                    message += word + " "

                # Color tags
                color_codes = {
                    '[reset]': '\033[0m',
                    '[red]': '\033[91m',
                    '[green]': '\033[92m',
                    '[yellow]': '\033[93m',
                    '[blue]': '\033[94m',
                    '[magenta]': '\033[95m',
                    '[cyan]': '\033[96m',
                    '[white]': '\033[97m'
                }

                # Replace color tags in message
                for tag, ansi in color_codes.items():
                    message = message.replace(tag, ansi)

                print(message + '\033[0m')  # Make sure to reset color after print
            elif cmd[0] == '0x06':  # HALT
                print("Program halted.", file=log_file)
                return  # Halt the execution
            elif cmd[0] == '0x07':  # SUB
                if len(cmd) < 4:
                    raise TypeError("SUB not given enough arguments")
                self.regs[cmd[3]] = self.regs[cmd[1]] - self.regs[cmd[2]]
            elif cmd[0] == '0x08':  # MULT
                if len(cmd) < 4:
                    raise TypeError("MULT not given enough arguments")
                self.regs[cmd[3]] = self.regs[cmd[1]] * self.regs[cmd[2]]
            elif cmd[0] == '0x09':  # DIV
                if len(cmd) < 4:
                    raise TypeError("DIV not given enough arguments")
                if self.regs[cmd[2]] == 0:
                    raise ZeroDivisionError("Division by zero")
                self.regs[cmd[3]] = self.regs[cmd[1]] // self.regs[cmd[2]]
            elif cmd[0] == '0x0A':  # MOD
                if len(cmd) < 4:
                    raise TypeError("MOD not given enough arguments")
                self.regs[cmd[3]] = self.regs[cmd[1]] % self.regs[cmd[2]]
            elif cmd[0] == '0x0B':  # AND
                if len(cmd) < 4:
                    raise TypeError("AND not given enough arguments")
                self.regs[cmd[3]] = self.regs[cmd[1]] & self.regs[cmd[2]]
            elif cmd[0] == '0x0C':  # OR
                if len(cmd) < 4:
                    raise TypeError("OR not given enough arguments")
                self.regs[cmd[3]] = self.regs[cmd[1]] | self.regs[cmd[2]]
            elif cmd[0] == '0x0D':  # XOR
                if len(cmd) < 4:
                    raise TypeError("XOR not given enough arguments")
                self.regs[cmd[3]] = self.regs[cmd[1]] ^ self.regs[cmd[2]]
            elif cmd[0] == '0x0E':  # NOT
                if len(cmd) < 3:
                    raise TypeError("NOT not given enough arguments")
                self.regs[cmd[2]] = ~self.regs[cmd[1]]
            elif cmd[0] == '0x0F':  # EXEC
                if len(cmd) < 2:
                    raise TypeError("EXEC not given enough arguments")
                if cmd[1].startswith("/"):
                    app = AppRunner(Disk.read_data_from_disk(os.path.basename(cmd[1]), os.path.dirname(cmd[1])), self.mode)
                    app.run()
                else:
                    app = AppRunner(Disk.read_data_from_disk(cmd[1], self.cwd), self.cwd, self.mode)
                    app.run()
            elif cmd[0] == '0x10':  # EXPY
                if len(cmd) < 2:
                    raise TypeError("EXPY not given enough arguments")
                if cmd[1].startswith("/"):
                    data = Disk.read_data_from_disk(os.path.basename(cmd[1]), os.path.dirname(cmd[1]))
                else:
                    data = Disk.read_data_from_disk(cmd[1], self.cwd)
                if not data:
                    raise FileNotFoundError(f"Could not find python file: '{cmd[1]}'")
                exec(data, {'__name__': '__main__', 'GUI': GUI})
            else:
                raise self.InvalidInstructionError(f"Unknown instruction '{cmd[0]}'.")
            pc += 1
        print("Program Exited without HALT", file=log_file)


class AppReader:
    class NeapExecutionError(Exception): pass
    class InvalidInstructionError(NeapExecutionError): pass

    def __init__(self, app_path, mode: Literal['safe', 'debug', 'normal'] = 'safe', log_file=sys.stderr):
        self.mode = mode
        self.files = app_path + '/Files/'
        self.exe = self.files + 'Executable/' + os.path.basename(app_path).split('.')[0]
        self.resources = self.files + 'Resources/'
        self.info = self.files + 'Info.prop'
        self.image = self.get_image(app_path)
        self.log_file = log_file

    @staticmethod
    def get_image(app_path):
        files = app_path + '/Files/'
        resources = files + 'Resources/'
        data = Disk.read_data_from_disk("Info.prop", files)
        data = json.loads(data)
        if not isinstance(data, dict):
            raise TypeError("Info.prop is not dict styled.")
        if "image" in data.keys():
            image = data["image"]
            img_data = Disk.read_data_from_disk(image, resources)
            if img_data:
                fake_file = io.BytesIO(GlobalUtils.svgToPng(img_data, 2))
                image = pygame.image.load(fake_file)
            else:
                raise FileNotFoundError("Image file not found. Please put image in Resources folder.")
            return image
        return

    def run(self):
        exe_code = Disk.read_data_from_disk(os.path.basename(self.exe), self.files + 'Executable').decode("utf-8")
        if not exe_code:
            raise FileNotFoundError("Executable not found")
        app = AppRunner(exe_code, self.files + "Executable", self.mode)
        app.run(log_file=self.log_file)


def main() -> None:
    Disk.load()
    app = AppRunner(r"""!8-bit-code

0x10 terminal-main.py
0x06
""", "/Applications/Terminal.neap/Files/Resources")
    app.run()

if __name__ == "__main__":
    main()
