from typing import Optional
import pygame
from fireboy_watergirl.settings import FIRE, WATER, FIRE_COLOR, WATER_COLOR


class ExitDoor(pygame.sprite.Sprite):
    """
    An exit door that a player must reach to win.

    A door may require one or two PressurePlates to be latched before it opens.
    If required_button_id is None the door is always open.
    If required_button_id_2 is also set, BOTH buttons must be latched.
    """

    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        element: str,
        required_button_id: Optional[str] = None,
        required_button_id_2: Optional[str] = None,
    ):
        super().__init__()
        self.element = element
        self.required_button_id   = required_button_id
        self.required_button_id_2 = required_button_id_2
        self.open: bool = required_button_id is None

        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        self._draw_door()
        self.rect = self.image.get_rect(topleft=(x, y))

    def _draw_door(self) -> None:
        self.image.fill((0, 0, 0, 0))
        base_color = FIRE_COLOR if self.element == FIRE else WATER_COLOR
        w, h = self.image.get_size()

        if self.open:
            r, g, b = base_color
            pygame.draw.rect(self.image, (r, g, b, 140), (0, 0, w, h))
            pygame.draw.rect(self.image, base_color, (0, 0, w, h), 3)
            mid_x = w // 2
            arrow_pts = [(mid_x, 6), (mid_x - 8, 20), (mid_x + 8, 20)]
            pygame.draw.polygon(self.image, (255, 255, 255), arrow_pts)
        else:
            r, g, b = base_color
            dark = (r // 3, g // 3, b // 3)
            pygame.draw.rect(self.image, (*dark, 230), (0, 0, w, h))
            pygame.draw.rect(self.image, base_color, (0, 0, w, h), 3)
            pygame.draw.line(self.image, (200, 50, 50), (6, 6), (w - 6, h - 6), 3)
            pygame.draw.line(self.image, (200, 50, 50), (w - 6, 6), (6, h - 6), 3)

    def set_open(self, is_open: bool) -> None:
        if is_open != self.open:
            self.open = is_open
            self._draw_door()
