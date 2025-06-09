import pygame
from _core import GlobalUtils


class Window(pygame.Surface):
    def __init__(self, title, size, pos=(0, 0), font="Courier New", font_size=16):
        # Initialize as a pygame Surface
        pygame.init()
        super().__init__(size, pygame.SRCALPHA)

        self._drag_offset = None
        self._rect = self.get_rect(topleft=pos)
        self._title = title
        self._bar_height = 30
        self._dragging = False
        self.green = (self.get_width() - 10, 15)
        self.yellow = (self.get_width() - 25, 15)
        self.red = (self.get_width() - 40, 15)
        self.fullscreen = False
        self.font = pygame.font.SysFont(font, font_size)

        # Set the window background
        self.fill((30, 30, 30))  # Default window content color

    def blit(self, source, dest, area=None, special_flags: int = 0):
        pygame.Surface.blit(self, source=source, dest=(dest[0], dest[1] + self._bar_height), area=area, special_flags=special_flags)

    def _blit(self, source, dest, area=None, special_flags: int = 0):
        pygame.Surface.blit(self, source=source, dest=dest, area=area, special_flags=special_flags)

    def draw(self, parent_surface):
        # Replace the title bar area with transparent pixels
        titlebar_area = pygame.Surface((self._rect.width, self._bar_height), pygame.SRCALPHA)
        titlebar_area.fill((0, 0, 0))  # Transparent surface
        self._blit(titlebar_area, (0, 0))
        self.set_colorkey((0, 0, 0))

        # Redraw the title bar
        GlobalUtils.draw_rect(
            self, (60, 60, 60), (0, 0, self._rect.width, self._bar_height),
            brtl=10, brtr=10
        )

        # Title text
        title_text = self.font.render(self._title, True, (255, 255, 255))
        self._blit(title_text, (10, 5))

        self.green = [self.get_width() - 10, 15]
        self.yellow = [self.get_width() - 25, 15]
        self.red = [self.get_width() - 40, 15]
        pygame.draw.circle(self, (255, 0  , 0), self.red, 5)  # Red
        pygame.draw.circle(self, (255, 204, 0), self.yellow, 5)  # Yellow
        pygame.draw.circle(self, (0  , 255, 0), self.green, 5)  # Green

        # Blit the window onto the main screen
        parent_surface.blit(self, self._rect.topleft)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.get_titlebar_rect().collidepoint(event.pos):
                self.green = GlobalUtils.sum_list([self.get_width() - 10, 15], self._rect.topleft)
                self.yellow = GlobalUtils.sum_list([self.get_width() - 25, 15], self._rect.topleft)
                self.red = GlobalUtils.sum_list([self.get_width() - 40, 15], self._rect.topleft)
                if GlobalUtils.distance(*event.pos, *self.red) <= 5:
                    event = pygame.event.Event(pygame.QUIT)
                    return event
                self._dragging = True
                self._drag_offset = (event.pos[0] - self._rect.x, event.pos[1] - self._rect.y)
        elif event.type == pygame.MOUSEBUTTONUP:
            self._dragging = False
        elif event.type == pygame.MOUSEMOTION and self._dragging:
            self._rect.topleft = (event.pos[0] - self._drag_offset[0], event.pos[1] - self._drag_offset[1])
        return event

    def get_titlebar_rect(self):
        return pygame.Rect(self._rect.x, self._rect.y, self._rect.width, self._bar_height)
