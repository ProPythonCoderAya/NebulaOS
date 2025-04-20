from ..AppHandler import AppReader
from _core import GlobalUtils
import pygame
import sys
import os
import io
import time
from utils import *
import _core.Disk as Disk

pygame.init()
cwd = os.path.dirname(__file__)


def abspath(path):
    return os.path.join(cwd, path)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
GREEN = (0, 255, 0)
GRAY = (50, 50, 50)

# Main screen and background
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("NebulaOS Desktop")
background = pygame.image.load(abspath('Textures/Nebula.png')).convert_alpha()

# Sound loading
pygame.mixer.init()
start = pygame.mixer.Sound(abspath("Sounds/o95.wav"))

# Disk
Disk.load()  # Loads the disk

# App loading
apps = {}
parts = "/Applications".strip("/").split("/")
current = Disk.get_root()

for part in parts:
    if part in current["contents"] and current["contents"][part]["type"] == "dir":
        current = current["contents"][part]

for name, info in current["contents"].items():
    if info["type"] == "dir" and name.endswith(".neap"):
        apps[name] = info

# Fonts
font_big = pygame.font.SysFont("Courier New", 48)
font_small = pygame.font.SysFont("Courier New", 24)

# Mouse
mouse_size = (25, 25)
cursors = {
    'Mouse': pygame.transform.scale(pygame.image.load(abspath('Textures/Mouse/Mouse.png')).convert_alpha(), mouse_size),
    'Hand': pygame.transform.scale(pygame.image.load(abspath('Textures/Mouse/Hand.png')).convert_alpha(), mouse_size),
    'Drag': pygame.transform.scale(pygame.image.load(abspath('Textures/Mouse/Drag.png')).convert_alpha(), mouse_size)
}
mouse_offset = cursors['Mouse'].get_width() / 4

# Clock
clock = pygame.time.Clock()


def draw(pos):
    """Simple draw function that draws apps, 'app bar', and the time."""
    # Set the cursor
    cursor = "Mouse"

    # Get the mouse position
    mouse_pos = pygame.mouse.get_pos()

    # App bar
    draw_rounded_rect(WIN, GRAY, (0, HEIGHT - 50, WIDTH, 60), 10, 200)

    # Apps
    x, y = 10, 10
    for app_name, _ in apps.items():
        app_path = f"/Applications/{app_name}"
        app_image = AppReader.get_image(AppReader, app_path)
        WIN.blit(app_image, (x, y))
        x += app_image.get_width() + 5
        y += app_image.get_height() + 5
        if app_image.get_rect().collidepoint(mouse_pos):
            cursor = "Hand"
            if pygame.mouse.get_pressed()[0]:
                cursor = "Drag"

    # Clock
    current_time = time.strftime("%H:%M")
    clock_text = font_small.render(current_time, True, WHITE)
    WIN.blit(clock_text, ((WIDTH - 10) - clock_text.get_width(), HEIGHT - clock_text.get_height()))

    # Check if left mouse button is pressed
    if pygame.mouse.get_pressed()[0]:
        # Calculate the width and height based on the starting position and current mouse position
        width = mouse_pos[0] - pos[0]
        height = mouse_pos[1] - pos[1]
        color = (255, 255, 255)
        thickness = 1
        trans = 100

        # Draw the rectangle based on mouse drag direction
        if width < 0 and height < 0:  # Mouse moved up-left
            x, y, w, h = mouse_pos[0], mouse_pos[1], -width, -height
        elif width < 0:  # Mouse moved left
            x, y, w, h = mouse_pos[0], pos[1], -width, height
        elif height < 0:  # Mouse moved up
            x, y, w, h = pos[0], mouse_pos[1], width, -height
        else:  # Mouse moved down-right
            x, y, w, h = pos[0], pos[1], width, height
        draw_rounded_rect(WIN, color, (x, y, w, h), 0, trans, 0)
        pygame.draw.rect(WIN, color, (x, y, w, h), thickness)

    # Mouse
    WIN.blit(cursors[cursor], (mouse_pos[0] - mouse_offset, mouse_pos[1] - 5))


start.play()
# Fade the screen
pos = 0, 0
for alpha in range(255, 0, -5):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Disk.save()
            pygame.quit()
            sys.exit()
        elif event.type == pygame.VIDEORESIZE:
            background = pygame.transform.smoothscale(pygame.image.load(abspath('Textures/Nebula.png')).convert_alpha(),
                                                      (event.w, event.h))
            WIDTH, HEIGHT = event.w, event.h
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
    fade_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    fade_surface.fill(BLACK)
    fade_surface.set_alpha(alpha)
    WIN.blit(background, (0, 0))
    draw(pos)
    WIN.blit(fade_surface, (0, 0))
    pygame.display.update()
    clock.tick(30)

# Main loop
running = True
pygame.mouse.set_visible(0)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            background = pygame.transform.smoothscale(pygame.image.load(abspath('Textures/Nebula.png')).convert_alpha(),
                                                      (event.w, event.h))
            WIDTH, HEIGHT = event.w, event.h
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos

    # Background
    WIN.blit(background, (0, 0))

    # Draw the rest
    draw(pos)

    pygame.display.update()
    clock.tick(60)

Disk.save()
pygame.quit()
sys.exit()
