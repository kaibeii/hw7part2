import pygame
from fireboy_watergirl.settings import BUTTON_OFF, BUTTON_ON


class PressurePlate(pygame.sprite.Sprite):
    """
    A floor pressure plate that activates when a player stands on it.

    Attributes:
        button_id: string key linking this plate to one or more ExitDoors
        pressed:   True while at least one player is on the plate
        image:     surface that changes color based on pressed state
        rect:      collision / render rect (thin horizontal strip)
    """

    def __init__(self, x: int, y: int, w: int = 40, h: int = 8, button_id: str = ""):
        """
        Args:
            x, y:      top-left pixel position (should sit on top of a platform)
            w, h:      dimensions — keep h small (8px) so the plate sits on the surface
            button_id: unique identifier matched against ExitDoor.required_button_id
        """
        super().__init__()
        self.button_id = button_id
        self.pressed: bool = False
        self.image = pygame.Surface((w, h))
        self.image.fill(BUTTON_OFF)
        self.rect = self.image.get_rect(topleft=(x, y))

    def update_state(self, pressed: bool) -> None:
        if pressed:
            self.pressed = True
            self.image.fill(BUTTON_ON if self.pressed else BUTTON_OFF)
