from _core.AppHandler import GUI
import pygame


WIDTH, HEIGHT = 800, 600
WIN = GUI.Window("Terminal", (WIDTH, HEIGHT))
win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SRCALPHA)
font = pygame.font.SysFont("Courier New", 16)
text = ["(base) ayyan:ayayn $ "]

while True:
    for event in pygame.event.get():
        WIN.handle_event(event)
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                text.append("(base) ayyan:ayayn $ ")

    win.fill("black")

    WIN.fill((30, 30, 30))
    y = 0
    for line in text:
        WIN.blit(font.render(line, True, (255, 255, 255)), (0, y))
        y += 20

    WIN.draw(win)
    pygame.display.flip()
