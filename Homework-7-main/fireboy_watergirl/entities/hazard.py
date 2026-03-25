import pygame
from fireboy_watergirl.settings import FIRE, WATER, ACID, FIRE_COLOR, WATER_COLOR, ACID_COLOR


class HazardPool(pygame.sprite.Sprite):
    """
    A lethal pool of fire, water, or acid.

    Elemental death rules:
        FIRE  pool → kills WATER player (Watergirl dies in fire)
        WATER pool → kills FIRE  player (Fireboy dies in water)
        ACID  pool → kills both players

    Attributes:
        element: FIRE, WATER, or ACID
        image:   semi-transparent surface in the element's color
        rect:    collision / render rect
    """

    # Base colors per element
    _COLORS = {
        FIRE:  FIRE_COLOR,
        WATER: WATER_COLOR,
        ACID:  ACID_COLOR,
    }

    def __init__(self, x: int, y: int, w: int, h: int, element: str):
        """
        Args:
            x, y:    top-left pixel position
            w, h:    pixel dimensions of the pool
            element: settings.FIRE, settings.WATER, or settings.ACID
        """
        super().__init__()
        self.element = element
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        self._draw_pool()
        self.rect = self.image.get_rect(topleft=(x, y))

    def _draw_pool(self) -> None:
        """Fill surface with element color at 75% opacity."""
        r, g, b = self._COLORS.get(self.element, (150, 150, 150))
        self.image.fill((r, g, b, 190))

        # Draw a slightly brighter highlight strip along the top edge
        highlight = (min(r + 60, 255), min(g + 60, 255), min(b + 60, 255), 200)
        w = self.image.get_width()
        pygame.draw.rect(self.image, highlight, (0, 0, w, 4))

    def is_lethal_to(self, player_element: str) -> bool:
        """
        Return True if this pool kills a player of the given element.

        Args:
            player_element: the player's element (FIRE or WATER)
        """
        if self.element == ACID:
            return True
        if self.element == FIRE and player_element == WATER:
            return True
        if self.element == WATER and player_element == FIRE:
            return True
        return False
