from _core.AppHandler import GUI
import pygame


WIDTH, HEIGHT = 600, 400
WIN = GUI.Window("Hello", (WIDTH, HEIGHT))
win = pygame.display.set_mode((WIDTH*2, HEIGHT*2), pygame.SRCALPHA)

while True:
    for event in pygame.event.get():
        WIN.handle_event(event)
        if event.type == pygame.QUIT:
            exit()

    win.fill("black")

    WIN.fill((30, 30, 30))
    WIN.draw(win)

    pygame.display.flip()
