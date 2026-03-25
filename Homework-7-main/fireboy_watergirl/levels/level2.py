"""
level2.py — Level 2 layout data and factory function.

Puzzle concept (co-op required):
  Three buttons must all be latched before the doors open:
    - Button A: far LEFT platform (Fireboy's side) — unlocks Watergirl's door
    - Button B: far RIGHT platform (Watergirl's side) — unlocks Fireboy's door
    - Button C: CENTER upper platform — must be pressed by EITHER player

  The catch: hazards are placed on platforms mid-route, forcing players to
  time their jumps carefully. Players spawn in the CENTER this time and must
  split up to reach opposite sides.

Layout (top to bottom):
  - Doors are at the very top on the LEFT and RIGHT
  - Center upper platform has Button C (shared)
  - Left tower and right tower each have a button + hazard gauntlet
  - Floor has acid in the center blocking direct crossing
"""

from typing import Dict, List
import pygame

from fireboy_watergirl.entities.tile import Tile
from fireboy_watergirl.entities.hazard import HazardPool
from fireboy_watergirl.entities.button import PressurePlate
from fireboy_watergirl.entities.door import ExitDoor
from fireboy_watergirl.entities.player import Player
from fireboy_watergirl.settings import FIRE, WATER, ACID

# ---------------------------------------------------------------------------
# Spawn positions — both players start near the center this time
# ---------------------------------------------------------------------------
FIREBOY_START   = (310, 420)
WATERGIRL_START = (450, 420)

# ---------------------------------------------------------------------------
# Level data
# ---------------------------------------------------------------------------
#
# Platform surfaces used for button placement:
#   Left button platform:   y=300, surface y=300
#   Right button platform:  y=300, surface y=300
#   Center upper platform:  y=200, surface y=200
#   Door ledges:            y=100, surface y=100
#
LEVEL_DATA: List[dict] = [
    # --- Boundary ---
    {"type": "tile", "x": 0,   "y": 560, "w": 800, "h": 40},   # floor
    {"type": "tile", "x": 0,   "y": 0,   "w": 20,  "h": 600},  # left wall
    {"type": "tile", "x": 780, "y": 0,   "w": 20,  "h": 600},  # right wall
    {"type": "tile", "x": 0,   "y": 0,   "w": 800, "h": 20},   # ceiling

    # --- Floor platforms (players start here) ---
    {"type": "tile", "x": 20,  "y": 460, "w": 160, "h": 20},   # left floor shelf
    {"type": "tile", "x": 620, "y": 460, "w": 160, "h": 20},   # right floor shelf
    {"type": "tile", "x": 260, "y": 460, "w": 280, "h": 20},   # center floor platform

    # --- Mid-level platforms (vertical climbing route) ---
    {"type": "tile", "x": 20,  "y": 400, "w": 140, "h": 20},   # left mid-low
    {"type": "tile", "x": 640, "y": 400, "w": 140, "h": 20},   # right mid-low
    {"type": "tile", "x": 180, "y": 300, "w": 160, "h": 20},   # left button platform
    {"type": "tile", "x": 460, "y": 300, "w": 160, "h": 20},   # right button platform
    {"type": "tile", "x": 320, "y": 380, "w": 160, "h": 20},   # center mid platform

    # --- Upper level ---
    {"type": "tile", "x": 60,  "y": 200, "w": 180, "h": 20},   # left upper
    {"type": "tile", "x": 560, "y": 200, "w": 180, "h": 20},   # right upper
    {"type": "tile", "x": 300, "y": 200, "w": 200, "h": 20},   # center upper (button C here)

    # --- Door ledges ---
    {"type": "tile", "x": 20,  "y": 110, "w": 100, "h": 20},   # left door ledge
    {"type": "tile", "x": 680, "y": 110, "w": 100, "h": 20},   # right door ledge

    # --- Hazards ---
    # Floor hazards: acid in center gap forces players to use the platforms
    {"type": "hazard", "element": ACID,  "x": 180, "y": 540, "w": 80,  "h": 20},
    {"type": "hazard", "element": ACID,  "x": 540, "y": 540, "w": 80,  "h": 20},


    # Center mid platform: acid strip — both must jump over to reach center upper
    {"type": "hazard", "element": ACID,  "x": 360, "y": 360, "w": 60,  "h": 20},

    # Left button platform: fire pool on the far side (Watergirl coming from right must avoid)
    {"type": "hazard", "element": FIRE,  "x": 720, "y": 380, "w": 60,  "h": 20},

    # Right button platform: water pool on the far side
    {"type": "hazard", "element": WATER, "x": 20,  "y": 380, "w": 60,  "h": 20},

    # --- Pressure plates (all latch — stay on after pressed) ---
    # Button A: LEFT button platform (surface y=300) → y = 300-12 = 288
    # Unlocks Watergirl's door — Fireboy crosses to left side to press this
    {"type": "button", "x": 200, "y": 288, "w": 70, "h": 12, "id": "btn-a"},

    # Button B: RIGHT button platform (surface y=300) → y = 300-12 = 288
    # Unlocks Fireboy's door — Watergirl crosses to right side to press this
    {"type": "button", "x": 550, "y": 288, "w": 70, "h": 12, "id": "btn-b"},

    # Button C: CENTER upper platform (surface y=200) → y = 200-12 = 188
    # Required by BOTH doors — either player can press it
    {"type": "button", "x": 350, "y": 188, "w": 90, "h": 12, "id": "btn-c"},

    # --- Exit doors ---
    # Fireboy's door (red) — top-left — needs Button B (right) AND Button C (center)
    {"type": "door", "element": FIRE,  "x": 28,  "y": 45, "w": 44, "h": 65,
     "button_id": "btn-b", "button_id_2": "btn-c"},
    # Watergirl's door (blue) — top-right — needs Button A (left) AND Button C (center)
    {"type": "door", "element": WATER, "x": 728, "y": 45, "w": 44, "h": 65,
     "button_id": "btn-a", "button_id_2": "btn-c"},
]


# ---------------------------------------------------------------------------
# Factory function
# ---------------------------------------------------------------------------

def load_level() -> Dict[str, object]:
    """
    Instantiate all sprites for Level 2 and return them in named groups.
    Called by Game._start_level() when level 2 is loaded.
    """
    tiles   = pygame.sprite.Group()
    hazards = pygame.sprite.Group()
    buttons = pygame.sprite.Group()
    doors   = pygame.sprite.Group()

    for obj in LEVEL_DATA:
        t = obj["type"]
        if t == "tile":
            tiles.add(Tile(obj["x"], obj["y"], obj["w"], obj["h"]))
        elif t == "hazard":
            hazards.add(HazardPool(obj["x"], obj["y"], obj["w"], obj["h"], obj["element"]))
        elif t == "button":
            buttons.add(PressurePlate(obj["x"], obj["y"], obj["w"], obj["h"], obj["id"]))
        elif t == "door":
            doors.add(ExitDoor(
                obj["x"], obj["y"], obj["w"], obj["h"],
                obj["element"],
                obj.get("button_id"),
                obj.get("button_id_2"),
            ))

    fireboy   = Player(FIREBOY_START[0], FIREBOY_START[1], FIRE)
    watergirl = Player(WATERGIRL_START[0], WATERGIRL_START[1], WATER)

    return {
        "tiles":     tiles,
        "hazards":   hazards,
        "buttons":   buttons,
        "doors":     doors,
        "fireboy":   fireboy,
        "watergirl": watergirl,
    }
