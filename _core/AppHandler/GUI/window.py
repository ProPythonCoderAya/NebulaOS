import pygame
from _core import GlobalUtils


class Window(pygame.Surface):
    def __init__(self, title, size, pos=(0, 0)):
        # Initialize as a pygame Surface
        pygame.init()
        super().__init__(size, pygame.SRCALPHA)

        self._drag_offset = None
        self._rect = self.get_rect(topleft=pos)
        self._title = title
        self._bar_height = 30
        self._dragging = False

        # Set the window background
        self.fill((30, 30, 30))  # Default window content color

    def draw(self, parent_surface):
        # Replace the title bar area with transparent pixels
        titlebar_area = pygame.Surface((self._rect.width, self._bar_height), pygame.SRCALPHA)
        titlebar_area.fill((0, 0, 0))  # Transparent surface
        self.blit(titlebar_area, (0, 0))
        self.set_colorkey((0, 0, 0))

        # Redraw the title bar
        GlobalUtils.draw_rect(
            self, (60, 60, 60), (0, 0, self._rect.width, self._bar_height),
            brtl=10, brtr=10
        )

        # Title text
        font = pygame.font.SysFont("Courier New", 16)
        title_text = font.render(self._title, True, (255, 255, 255))
        self.blit(title_text, (10, 5))

        # Blit the window onto the main screen
        parent_surface.blit(self, self._rect.topleft)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.get_titlebar_rect().collidepoint(event.pos):
                self._dragging = True
                self._drag_offset = (event.pos[0] - self._rect.x, event.pos[1] - self._rect.y)
        elif event.type == pygame.MOUSEBUTTONUP:
            self._dragging = False
        elif event.type == pygame.MOUSEMOTION and self._dragging:
            self._rect.topleft = (event.pos[0] - self._drag_offset[0], event.pos[1] - self._drag_offset[1])

    def get_titlebar_rect(self):
        return pygame.Rect(self._rect.x, self._rect.y, self._rect.width, self._bar_height)
