import pygame
from fireboy_watergirl.settings import TILE_COLOR


class Tile(pygame.sprite.Sprite):
    """
    Solid rectangular platform or wall.
    All four sides block player movement (no one-way pass-through).

    Attributes:
        image: pygame.Surface filled with tile color
        rect:  pygame.Rect used for collision and rendering
    """

    def __init__(self, x: int, y: int, w: int, h: int, color: tuple = TILE_COLOR):
        """
        Args:
            x, y: top-left pixel position
            w, h: pixel dimensions
            color: RGB fill color (defaults to TILE_COLOR)
        """
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
