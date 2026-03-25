import pygame
from fireboy_watergirl.settings import (
    GRAVITY, JUMP_STRENGTH, MAX_FALL_SPEED, PLAYER_SPEED,
    PLAYER_W, PLAYER_H, FIRE, WATER, FIRE_COLOR, WATER_COLOR,
)


class Player(pygame.sprite.Sprite):
    """
    Represents either Fireboy or Watergirl.

    Attributes:
        element:   'fire' (Fireboy) or 'water' (Watergirl)
        vel_x:     horizontal velocity in pixels/frame
        vel_y:     vertical velocity in pixels/frame
        on_ground: True when resting on a tile surface
        alive:     False when the player has touched a lethal hazard
        at_door:   True when overlapping an open exit door this frame
    """

    # Arrow-key bindings for Fireboy
    _FIRE_KEYS = {
        "left":  pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "jump":  pygame.K_UP,
    }

    # WASD bindings for Watergirl
    _WATER_KEYS = {
        "left":  pygame.K_a,
        "right": pygame.K_d,
        "jump":  pygame.K_w,
    }

    def __init__(self, x: int, y: int, element: str):
        """
        Args:
            x, y:    top-left spawn position in pixels
            element: settings.FIRE or settings.WATER
        """
        super().__init__()
        self.element = element

        # Build sprite surface with a simple body + element icon
        self.image = pygame.Surface((PLAYER_W, PLAYER_H), pygame.SRCALPHA)
        self._draw_player()
        self.rect = self.image.get_rect(topleft=(x, y))

        self.vel_x: float = 0.0
        self.vel_y: float = 0.0
        self.on_ground: bool = False

        self.alive: bool = True
        self.at_door: bool = False

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def _draw_player(self) -> None:
        """Render player body and element indicator onto self.image."""
        body_color = FIRE_COLOR if self.element == FIRE else WATER_COLOR

        # Body rectangle
        pygame.draw.rect(self.image, body_color, (0, 12, PLAYER_W, PLAYER_H - 12))

        # Head (circle)
        head_color = tuple(min(c + 40, 255) for c in body_color)
        pygame.draw.circle(self.image, head_color, (PLAYER_W // 2, 10), 10)

        # Element icon drawn on the body
        if self.element == FIRE:
            # Small flame: triangle pointing up
            pts = [
                (PLAYER_W // 2, 14),
                (PLAYER_W // 2 - 6, 28),
                (PLAYER_W // 2 + 6, 28),
            ]
            pygame.draw.polygon(self.image, (255, 200, 0), pts)
        else:
            # Water droplet: circle with a point at the top
            pygame.draw.circle(self.image, (180, 220, 255), (PLAYER_W // 2, 24), 6)
            pts = [
                (PLAYER_W // 2, 14),
                (PLAYER_W // 2 - 5, 22),
                (PLAYER_W // 2 + 5, 22),
            ]
            pygame.draw.polygon(self.image, (180, 220, 255), pts)

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        """
        Read keyboard state and update vel_x; trigger jump if on ground.
        Does NOT move the rect — that happens in update() + resolve_*().
        """
        bindings = self._FIRE_KEYS if self.element == FIRE else self._WATER_KEYS

        self.vel_x = 0.0
        if keys[bindings["left"]]:
            self.vel_x = -PLAYER_SPEED
        if keys[bindings["right"]]:
            self.vel_x = PLAYER_SPEED

        # Jump: only when standing on something
        if keys[bindings["jump"]] and self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False

    # ------------------------------------------------------------------
    # Physics
    # ------------------------------------------------------------------

    def update(self) -> None:
        """
        Apply gravity to vel_y.  The rect is NOT moved here; collision
        resolution in resolve_x / resolve_y does the actual movement so
        the two axes can be handled independently.
        """
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

    def resolve_x(self, tiles: pygame.sprite.Group) -> None:
        """
        Move rect horizontally by vel_x, then push out of any overlapping tiles.
        Zeroes vel_x on collision.
        """
        self.rect.x += int(self.vel_x)
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vel_x > 0:               # moving right → push left
                    self.rect.right = tile.rect.left
                elif self.vel_x < 0:             # moving left → push right
                    self.rect.left = tile.rect.right
                self.vel_x = 0.0

    def resolve_y(self, tiles: pygame.sprite.Group) -> None:
        """
        Move rect vertically by vel_y, then push out of any overlapping tiles.
        Sets on_ground = True when landing on top of a tile.
        """
        self.rect.y += int(self.vel_y)
        self.on_ground = False
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vel_y > 0:               # falling → land on top
                    self.rect.bottom = tile.rect.top
                    self.on_ground = True
                elif self.vel_y < 0:             # jumping → hit ceiling
                    self.rect.top = tile.rect.bottom
                self.vel_y = 0.0

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    def kill_player(self) -> None:
        """Mark the player as dead.  Game detects this and triggers GAME_OVER."""
        self.alive = False
