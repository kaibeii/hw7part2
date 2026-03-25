from typing import Optional
import pygame
from fireboy_watergirl.settings import FIRE, WATER, FIRE_COLOR, WATER_COLOR


class ExitDoor(pygame.sprite.Sprite):
    """
    An exit door that a player must reach to win.

    Each door is associated with one element (FIRE or WATER).
    Only the matching player can use it as a win condition.

    A door may require a PressurePlate to be held before it becomes passable.
    If required_button_id is None the door is always open.

    Attributes:
        element:            FIRE (Fireboy's door) or WATER (Watergirl's door)
        required_button_id: button_id of the PressurePlate that unlocks this door,
                            or None for an always-open door
        open:               runtime state — True when the door is passable
        image:              surface drawn with element color and open/closed indicator
        rect:               collision / render rect
    """

    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        element: str,
        required_button_id: Optional[str] = None,
    ):
        """
        Args:
            x, y:               top-left pixel position
            w, h:               pixel dimensions
            element:            settings.FIRE or settings.WATER
            required_button_id: links to a PressurePlate; None = always open
        """
        super().__init__()
        self.element = element
        self.required_button_id = required_button_id
        # Doors with no button requirement start open; others start closed
        self.open: bool = required_button_id is None

        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        self._draw_door()
        self.rect = self.image.get_rect(topleft=(x, y))

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def _draw_door(self) -> None:
        """Render door appearance based on element and open/closed state."""
        self.image.fill((0, 0, 0, 0))  # clear

        base_color = FIRE_COLOR if self.element == FIRE else WATER_COLOR
        w, h = self.image.get_size()

        if self.open:
            # Open: bright element color with a semi-transparent fill to show passage
            r, g, b = base_color
            pygame.draw.rect(self.image, (r, g, b, 140), (0, 0, w, h))
            # Door frame (solid outline)
            pygame.draw.rect(self.image, base_color, (0, 0, w, h), 3)
            # Arrow pointing up (enter here)
            mid_x = w // 2
            arrow_pts = [
                (mid_x, 6),
                (mid_x - 8, 20),
                (mid_x + 8, 20),
            ]
            pygame.draw.polygon(self.image, (255, 255, 255), arrow_pts)
        else:
            # Closed: dark fill with a lock symbol
            r, g, b = base_color
            dark = (r // 3, g // 3, b // 3)
            pygame.draw.rect(self.image, (*dark, 230), (0, 0, w, h))
            pygame.draw.rect(self.image, base_color, (0, 0, w, h), 3)
            # Draw an "X" to indicate locked
            pygame.draw.line(self.image, (200, 50, 50), (6, 6), (w - 6, h - 6), 3)
            pygame.draw.line(self.image, (200, 50, 50), (w - 6, 6), (6, h - 6), 3)

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    def set_open(self, is_open: bool) -> None:
        """
        Update open/closed state and redraw the door visual.
        Called every frame by Game._check_buttons().

        Args:
            is_open: True if the linked button is currently pressed (or no button required)
        """
        if is_open != self.open:
            self.open = is_open
            self._draw_door()
