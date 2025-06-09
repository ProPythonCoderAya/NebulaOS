from System import parse_cmd, GUI
import pygame
import sys
import json
import io
import platform
pygame.init()


def custom_input(msg):
    print(msg, end="", file=sys.__stdout__)
    return input()


global command_text, user, user_data, sign, user_home, current_path
WIDTH, HEIGHT = 800, 600
font = "Jetbrains Mono"
WIN = GUI.Window("Terminal", (WIDTH, HEIGHT), font=font, font_size=13)
win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SRCALPHA)
HEIGHT -= 30
font = pygame.font.SysFont(font, 13)
user = sys.argv[1]
user_data = json.loads(sys.argv[2])
sign = "#" if user == "root" else "$"
user_home = user_data["home"]
current_path = user_home
path = current_path.split("/")[-1]
if current_path == user_home:
    path = "~"
if not path:
    path = "/"
base = f"(base) {platform.node().split('.')[0]}:{path} {user}{sign} "
typed_text = ""
text = [""]
commands_run = [""]
index = -1
displayed_text = text
run = True
clock = pygame.time.Clock()

while run:
    for event in pygame.event.get():
        event = WIN.handle_event(event)
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                commands_run.append(typed_text)
                stdout = io.StringIO()
                sys.stdout = stdout
                result = parse_cmd(typed_text, current_path, user, user_data, "GUI", input_func=custom_input)
                if result:
                    if isinstance(result, str):
                        current_path = result
                    if result == -1:
                        break
                sys.stdout = sys.__stdout__
                stdout.seek(0)
                data = stdout.read()
                for line in data.split("\n"):
                    text.append(line)
                typed_text = ""
            elif event.key == pygame.K_BACKSPACE:
                typed_text = typed_text[:-1]
            elif event.key == pygame.K_UP:
                index -= 1
                if -index > len(commands_run):
                    index = -len(commands_run)
                typed_text = commands_run[index]
            elif event.key == pygame.K_DOWN:
                index += 1
                if index >= 0:
                    typed_text = ""
                    index = 0
                else:
                    typed_text = commands_run[index]
            else:
                if event.unicode:
                    typed_text += event.unicode
    text[-1] = base + typed_text
    commands_run[-1] = typed_text

    path = current_path.split("/")[-1]

    if current_path == user_home:
        path = "~"
    if not path:
        path = "/"

    win.fill("black")

    base = f"(base) {platform.node().split('.')[0]}:{path} {user}{sign} "

    WIN.fill((30, 30, 30))
    y = 0
    displayed_text = text
    max_lines = HEIGHT // 20

    if len(text) > max_lines:
        displayed_text = displayed_text[len(text) - max_lines:]

    for i, line in enumerate(displayed_text):
        # Blinking cursor: "█" appears/disappears every ~500ms
        cursor = ""
        if i == len(displayed_text) - 1:
            cursor = "█" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
        WIN.blit(font.render(line + cursor, True, (255, 255, 255)), (0, y))
        y += 20

    WIN.draw(win)
    pygame.display.flip()
    clock.tick(60)
