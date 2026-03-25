"""
game.py — Game class: state machine, main loop, collision dispatch, HUD, and menus.

State machine:
    STATE_MENU  ──────► STATE_PLAYING ──► STATE_WIN       ──► STATE_MENU
                                      └─► STATE_GAME_OVER ──► STATE_MENU
"""

import sys
import pygame

from fireboy_watergirl.settings import (
    SCREEN_W, SCREEN_H, FPS, BG_COLOR, TITLE,
    WHITE, BLACK, FIRE_COLOR, WATER_COLOR,
    STATE_MENU, STATE_PLAYING, STATE_WIN, STATE_GAME_OVER,
    FIRE, WATER,
)
from fireboy_watergirl.levels.level1 import load_level


class Game:
    """
    Top-level game controller.

    Responsibilities:
        - Pygame initialisation and the display surface
        - State machine (menu / playing / win / game-over)
        - Per-frame update dispatch for physics, hazards, buttons, doors
        - Rendering all sprites and UI
    """

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        self.font_large  = pygame.font.SysFont("Arial", 52, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", 32, bold=True)
        self.font_small  = pygame.font.SysFont("Arial", 20)

        self.state = STATE_MENU

        # Level objects — populated by _start_level()
        self.tiles    = None
        self.hazards  = None
        self.buttons  = None
        self.doors    = None
        self.fireboy  = None
        self.watergirl = None

    # =========================================================================
    # Main loop
    # =========================================================================

    def run(self) -> None:
        """Entry point.  Runs until the window is closed."""
        while True:
            self.clock.tick(FPS)
            self._handle_global_events()

            if self.state == STATE_MENU:
                self._update_menu()
                self._draw_menu()
            elif self.state == STATE_PLAYING:
                self._update_playing()
                self._draw_playing()
            elif self.state == STATE_WIN:
                self._update_overlay()
                self._draw_playing()          # show level in background
                self._draw_win_overlay()
            elif self.state == STATE_GAME_OVER:
                self._update_overlay()
                self._draw_playing()          # show level in background
                self._draw_game_over_overlay()

            pygame.display.flip()

    # =========================================================================
    # Global events (quit, restart)
    # =========================================================================

    def _handle_global_events(self) -> None:
        """Handle QUIT and universal R-to-restart key."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.state != STATE_MENU:
                    self._start_level()

    # =========================================================================
    # Level initialisation
    # =========================================================================

    def _start_level(self) -> None:
        """
        Load all level sprites fresh and transition to STATE_PLAYING.
        Called on first start and on restart (R key or menu replay).
        """
        level = load_level()
        self.tiles     = level["tiles"]
        self.hazards   = level["hazards"]
        self.buttons   = level["buttons"]
        self.doors     = level["doors"]
        self.fireboy   = level["fireboy"]
        self.watergirl = level["watergirl"]
        self.state = STATE_PLAYING

    # =========================================================================
    # MENU state
    # =========================================================================

    def _update_menu(self) -> None:
        """Start game on ENTER or SPACE."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
            self._start_level()

    def _draw_menu(self) -> None:
        """Render the title screen."""
        # Background gradient: split red (left) / blue (right)
        left_surf  = pygame.Surface((SCREEN_W // 2, SCREEN_H))
        right_surf = pygame.Surface((SCREEN_W // 2, SCREEN_H))
        left_surf.fill((80, 25, 10))
        right_surf.fill((10, 30, 80))
        self.screen.blit(left_surf, (0, 0))
        self.screen.blit(right_surf, (SCREEN_W // 2, 0))

        # Title
        title_surf = self.font_large.render("Fireboy & Watergirl", True, WHITE)
        tx = SCREEN_W // 2 - title_surf.get_width() // 2
        self.screen.blit(title_surf, (tx, 120))

        # Subtitle
        sub = self.font_small.render("A co-op puzzle platformer", True, (200, 200, 200))
        self.screen.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, 186))

        # Controls block
        controls = [
            ("Fireboy",   "Arrow Keys  ←  →  ↑ jump", FIRE_COLOR),
            ("Watergirl", "A / D  move    W  jump",    WATER_COLOR),
        ]
        y_start = 260
        for name, keys_text, color in controls:
            name_surf = self.font_medium.render(name + ":", True, color)
            keys_surf = self.font_small.render(keys_text, True, WHITE)
            cx = SCREEN_W // 2
            self.screen.blit(name_surf, (cx - name_surf.get_width() // 2, y_start))
            self.screen.blit(keys_surf, (cx - keys_surf.get_width() // 2, y_start + 38))
            y_start += 90

        # Goal text
        goal = self.font_small.render(
            "Both players must reach their EXIT DOORS at the same time!", True, (220, 220, 100)
        )
        self.screen.blit(goal, (SCREEN_W // 2 - goal.get_width() // 2, 450))

        # Start prompt (blink using tick count)
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            start_surf = self.font_medium.render("Press  ENTER  to Start", True, WHITE)
            self.screen.blit(start_surf, (SCREEN_W // 2 - start_surf.get_width() // 2, 520))

        # Restart hint (not shown on menu, but show R key hint)
        r_hint = self.font_small.render("R = Restart  during play", True, (150, 150, 150))
        self.screen.blit(r_hint, (SCREEN_W // 2 - r_hint.get_width() // 2, 570))

    # =========================================================================
    # PLAYING state — update
    # =========================================================================

    def _update_playing(self) -> None:
        """
        One full frame of game logic:
          1. Input
          2. Physics (gravity + move)
          3. Platform collision (axis-separated)
          4. Hazard checks (death)
          5. Button checks (update pressed state)
          6. Door checks (update open state + player.at_door flag)
          7. Win / death detection
        """
        keys = pygame.key.get_pressed()

        for player in (self.fireboy, self.watergirl):
            player.at_door = False           # reset each frame
            player.handle_input(keys)
            player.update()                  # apply gravity
            player.resolve_x(self.tiles)
            player.resolve_y(self.tiles)

        self._check_hazards()
        self._check_buttons()
        self._check_doors()
        self._check_win_or_death()

    def _check_hazards(self) -> None:
        """Kill any player that overlaps a lethal hazard pool."""
        for player in (self.fireboy, self.watergirl):
            if not player.alive:
                continue
            for hazard in self.hazards:
                if player.rect.colliderect(hazard.rect) and hazard.is_lethal_to(player.element):
                    player.kill_player()
                    break

    def _check_buttons(self) -> None:
        """
        Determine which buttons are pressed this frame, then update door states.
        A button is only considered pressed when the player is on the ground and
        overlapping the plate — prevents false triggers while jumping overhead.
        """
        pressed_ids: set = set()

        for button in self.buttons:
            fb_on = (
                self.fireboy.on_ground and
                self.fireboy.rect.colliderect(button.rect)
            )
            wg_on = (
                self.watergirl.on_ground and
                self.watergirl.rect.colliderect(button.rect)
            )
            button.update_state(fb_on or wg_on)
            if button.pressed:
                pressed_ids.add(button.button_id)

        # Open/close doors based on pressed buttons
        for door in self.doors:
            if door.required_button_id is None:
                door.set_open(True)
            else:
                door.set_open(door.required_button_id in pressed_ids)

    def _check_doors(self) -> None:
        """
        Set player.at_door = True when the player overlaps their OPEN exit door.
        Only the matching element door counts (Fireboy → fire door, Watergirl → water door).
        """
        for door in self.doors:
            if not door.open:
                continue
            if door.element == FIRE and self.fireboy.rect.colliderect(door.rect):
                self.fireboy.at_door = True
            if door.element == WATER and self.watergirl.rect.colliderect(door.rect):
                self.watergirl.at_door = True

    def _check_win_or_death(self) -> None:
        """
        Win:        both players are at their open door on the same frame.
        Game over:  either player is dead.
        Win takes priority (both could technically collide and win at the exact
        frame a hazard kills them — unlikely but win is the better outcome).
        """
        if self.fireboy.at_door and self.watergirl.at_door:
            self.state = STATE_WIN
            return
        if not self.fireboy.alive or not self.watergirl.alive:
            self.state = STATE_GAME_OVER

    # =========================================================================
    # PLAYING state — draw
    # =========================================================================

    def _draw_playing(self) -> None:
        """
        Render the level.  Painter's order (back to front):
          1. Background
          2. Tiles
          3. Hazards
          4. Buttons
          5. Doors
          6. Players
          7. HUD
        """
        self.screen.fill(BG_COLOR)

        self.tiles.draw(self.screen)
        self.hazards.draw(self.screen)
        self.buttons.draw(self.screen)
        self.doors.draw(self.screen)

        # Players rendered individually (not in a group) so we can always draw both
        self.screen.blit(self.fireboy.image,   self.fireboy.rect)
        self.screen.blit(self.watergirl.image, self.watergirl.rect)

        self._draw_hud()

    def _draw_hud(self) -> None:
        """Render control labels and restart hint at the top of the screen."""
        # Fireboy label (left)
        fb_label = self.font_small.render("Fireboy: ← → ↑", True, FIRE_COLOR)
        self.screen.blit(fb_label, (25, 25))

        # Watergirl label (right)
        wg_label = self.font_small.render("Watergirl: A D W", True, WATER_COLOR)
        self.screen.blit(wg_label, (SCREEN_W - wg_label.get_width() - 25, 25))

        # Door status hints (center)
        fb_door = self._get_door(FIRE)
        wg_door = self._get_door(WATER)

        hints = []
        if fb_door and not fb_door.open:
            hints.append(("Fireboy's door: LOCKED", FIRE_COLOR))
        if wg_door and not wg_door.open:
            hints.append(("Watergirl's door: LOCKED", WATER_COLOR))

        y_hint = 25
        for text, color in hints:
            surf = self.font_small.render(text, True, color)
            self.screen.blit(surf, (SCREEN_W // 2 - surf.get_width() // 2, y_hint))
            y_hint += 22

        # Restart hint
        r_surf = self.font_small.render("R = Restart", True, (120, 120, 120))
        self.screen.blit(r_surf, (SCREEN_W // 2 - r_surf.get_width() // 2, SCREEN_H - 24))

    def _get_door(self, element: str):
        """Helper: return the first ExitDoor matching the given element, or None."""
        for door in self.doors:
            if door.element == element:
                return door
        return None

    # =========================================================================
    # Overlay states
    # =========================================================================

    def _update_overlay(self) -> None:
        """
        On WIN or GAME_OVER screens:
          ENTER / SPACE → return to menu
          R             → restart immediately (handled by _handle_global_events)
        """
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
            self.state = STATE_MENU

    def _draw_win_overlay(self) -> None:
        """Semi-transparent green overlay with WIN message."""
        self._draw_dimmed_overlay((20, 100, 20), 160)

        title = self.font_large.render("YOU WIN!", True, (100, 255, 100))
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 200))

        sub = self.font_medium.render("Both players escaped!", True, WHITE)
        self.screen.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, 280))

        self._draw_replay_prompt()

    def _draw_game_over_overlay(self) -> None:
        """Semi-transparent red overlay with GAME OVER message."""
        self._draw_dimmed_overlay((100, 10, 10), 160)

        title = self.font_large.render("GAME OVER", True, (255, 80, 80))
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 200))

        # Show which player died
        if not self.fireboy.alive and not self.watergirl.alive:
            msg = "Both players perished!"
        elif not self.fireboy.alive:
            msg = "Fireboy didn't make it..."
        else:
            msg = "Watergirl didn't make it..."

        sub = self.font_medium.render(msg, True, WHITE)
        self.screen.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, 280))

        self._draw_replay_prompt()

    def _draw_dimmed_overlay(self, color: tuple, alpha: int) -> None:
        """Draw a full-screen semi-transparent rectangle over the level."""
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((*color, alpha))
        self.screen.blit(overlay, (0, 0))

    def _draw_replay_prompt(self) -> None:
        """Blinking replay / menu prompt shown on WIN and GAME_OVER screens."""
        if (pygame.time.get_ticks() // 600) % 2 == 0:
            prompt = self.font_medium.render("ENTER = Menu    R = Restart", True, WHITE)
            self.screen.blit(prompt, (SCREEN_W // 2 - prompt.get_width() // 2, 370))
