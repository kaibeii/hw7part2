"""
level1.py — Level 1 layout data and factory function.

Puzzle concept (co-op required):
  Fireboy starts on the left, Watergirl on the right.
  Fireboy's exit door (red, top-left) is locked behind Button B on the RIGHT side.
  Watergirl's exit door (blue, top-right) is locked behind Button A on the LEFT side.
  Players must cross the center (avoiding hazards), each step on the OTHER's button,
  then both reach their door simultaneously to win.

Hazards:
  - Water pool on the floor (left-center) — kills Fireboy
  - Fire pool on the floor (right-center) — kills Watergirl
  - Acid pool on the center bridge — kills both
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
# Spawn positions
# ---------------------------------------------------------------------------
FIREBOY_START = (60, 435)
WATERGIRL_START = (680, 435)

# ---------------------------------------------------------------------------
# Level data — list of descriptor dicts parsed by load_level()
# ---------------------------------------------------------------------------
LEVEL_DATA: List[dict] = [
    # --- Boundary ---
    {"type": "tile", "x": 0,   "y": 560, "w": 800, "h": 40},   # floor
    {"type": "tile", "x": 0,   "y": 0,   "w": 20,  "h": 600},  # left wall
    {"type": "tile", "x": 780, "y": 0,   "w": 20,  "h": 600},  # right wall
    {"type": "tile", "x": 0,   "y": 0,   "w": 800, "h": 20},   # ceiling

    # --- Stepping platforms (players navigate these to cross the center) ---
    {"type": "tile", "x": 20,  "y": 480, "w": 200, "h": 20},   # left shelf
    {"type": "tile", "x": 180, "y": 400, "w": 180, "h": 20},   # mid-left step
    {"type": "tile", "x": 310, "y": 320, "w": 180, "h": 20},   # center bridge (acid on top)
    {"type": "tile", "x": 440, "y": 400, "w": 180, "h": 20},   # mid-right step
    {"type": "tile", "x": 580, "y": 480, "w": 200, "h": 20},   # right shelf

    # --- Upper platforms (path from shelf to door ledge) ---
    {"type": "tile", "x": 20,  "y": 240, "w": 200, "h": 20},   # left upper
    {"type": "tile", "x": 580, "y": 240, "w": 200, "h": 20},   # right upper
    {"type": "tile", "x": 20,  "y": 160, "w": 80,  "h": 20},   # left door ledge
    {"type": "tile", "x": 700, "y": 160, "w": 80,  "h": 20},   # right door ledge

    # --- Hazard pools ---
    # Water pool: kills Fireboy (left side of floor)
    {"type": "hazard", "element": WATER, "x": 220, "y": 540, "w": 90, "h": 20},
    # Fire pool: kills Watergirl (right side of floor)
    {"type": "hazard", "element": FIRE,  "x": 490, "y": 540, "w": 90, "h": 20},
    # Acid pool: on center bridge, kills both — players must jump over it
    {"type": "hazard", "element": ACID,  "x": 350, "y": 300, "w": 80, "h": 20},

    # --- Pressure plates (sit on top of left/right shelves) ---
    # Button A is on the LEFT shelf (near Fireboy's start) — unlocks Watergirl's door
    {"type": "button", "x": 180, "y": 472, "w": 40, "h": 8, "id": "btn-a"},
    # Button B is on the RIGHT shelf (near Watergirl's start) — unlocks Fireboy's door
    {"type": "button", "x": 580, "y": 472, "w": 40, "h": 8, "id": "btn-b"},

    # --- Exit doors (cross-linked: each door needs the OPPOSITE player's button) ---
    # Fireboy's door (fire/red) — top-left — requires Button B (right side)
    {"type": "door", "element": FIRE,  "x": 28,  "y": 95,  "w": 44, "h": 65, "button_id": "btn-b"},
    # Watergirl's door (water/blue) — top-right — requires Button A (left side)
    {"type": "door", "element": WATER, "x": 708, "y": 95,  "w": 44, "h": 65, "button_id": "btn-a"},
]


# ---------------------------------------------------------------------------
# Factory function
# ---------------------------------------------------------------------------

def load_level() -> Dict[str, object]:
    """
    Instantiate all sprites for Level 1 and return them in named groups.
    Called by Game._start_level() each time a new game begins (including restarts).

    Returns a dict with keys:
        tiles, hazards, buttons, doors — pygame.sprite.Group instances
        fireboy, watergirl             — Player instances
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
                obj["element"], obj.get("button_id"),
            ))

    fireboy   = Player(FIREBOY_START[0],   FIREBOY_START[1],   FIRE)
    watergirl = Player(WATERGIRL_START[0], WATERGIRL_START[1], WATER)

    return {
        "tiles":     tiles,
        "hazards":   hazards,
        "buttons":   buttons,
        "doors":     doors,
        "fireboy":   fireboy,
        "watergirl": watergirl,
    }
