# Fireboy & Watergirl (Pygame Clone) — Phase 2

## Project Received

A two-player local co-op puzzle platformer built with Python and Pygame, implementing
the classic Fireboy & Watergirl game mechanic. The project was in a functional but
buggy state — the core structure (state machine, entity classes, level loading) was
well-architected and clean, but several gameplay bugs made it frustrating or broken
to play.

## How to Run

```bash
pip install -r requirements.txt
python -m fireboy_watergirl
```

Requires Python 3.8–3.13. **Does not work on Python 3.14** — pygame has not yet
released a compatible wheel. Use `py -3.11 -m pip install pygame>=2.1.0` and
`py -3.11 -m fireboy_watergirl` if you have multiple Python versions installed.

## Controls

| Player    | Move Left | Move Right | Jump |
|-----------|-----------|------------|------|
| Fireboy   | ←         | →          | ↑    |
| Watergirl | A         | D          | W    |

**R** — restart the current level at any time  
**N** — advance to next level (shown on win screen)  
**ENTER** — start game / return to menu

## Rules

- **Fireboy** (red) is immune to fire pools but **dies in water**.
- **Watergirl** (blue) is immune to water pools but **dies in fire**.
- **Acid** (green) kills both players.
- Both players must reach their **exit door simultaneously** to win.
  - Fireboy's door is **red** (top-left).
  - Watergirl's door is **blue** (top-right).
- **Buttons latch** — once stepped on they stay pressed permanently.

## Level 1 Puzzle

The exit doors are locked behind pressure plates on the **opposite** side of the map:
- Fireboy's red door opens when the **right-side button** is pressed (Watergirl's territory).
- Watergirl's blue door opens when the **left-side button** is pressed (Fireboy's territory).

Both players must cross the hazard-filled center, step on each other's button,
and enter their doors **at the same time**.

## Level 2 Puzzle

Three buttons must all be latched before either door opens:
- **Button A** (left platform) + **Button C** (center upper) → opens Watergirl's door
- **Button B** (right platform) + **Button C** (center upper) → opens Fireboy's door

Players spawn in the center and must split up. Each player crosses to the opposite
side to press their button, then both must reach the center upper platform to press
Button C, then climb to their doors simultaneously.

---

## What State the Code Was In

The project had a solid, readable architecture with well-named classes and clean
separation of concerns. However several bugs made it difficult or impossible to play
correctly.

### Bugs Fixed

**`player.py` — Dead players still accepted input and ran physics**
After being killed, `handle_input()`, `update()`, and `resolve_*()` still ran,
causing dead players to drift or fall through the level. Added `if not self.alive: return`
guards to all four methods.

**`player.py` — Sub-pixel gravity truncation blocked jumping**
`vel_y` increases by `GRAVITY = 0.6` per frame. `resolve_y()` applied `int(self.vel_y)`
which is `int(0.6) = 0` — so the player never moved vertically, `on_ground` was never
set `True`, and jumping was blocked. Fixed with a `_remainder_y` accumulator that
carries fractional pixels across frames.

**`player.py` — `resolve_y` condition `vel_y > 0` prevented landing at vel_y == 0**
After a collision resets `vel_y` to 0.0, the condition `if self.vel_y > 0` would fail
on the next frame, so the player was not pushed to the tile surface and `on_ground`
stayed False. Changed to `vel_y >= 0`.

**`game.py` — Menu and overlay transitions used `get_pressed()` (held state)**
`get_pressed()` returns True for every frame a key is held. Pressing ENTER to start
the game immediately also registered as ENTER on the overlay, skipping past
WIN/GAME_OVER screens instantly. Fixed by moving all state transitions to `KEYDOWN`
events in `_handle_global_events()`.

**`game.py` — Dead players could activate buttons and trigger doors**
A dead player's frozen rect could overlap a button keeping it pressed, or overlap a
door tile triggering a spurious WIN. Fixed by adding `alive` guards in
`_check_buttons()` and `_check_doors()`.

**`game.py` — `on_ground` check on buttons caused flickering doors**
Buttons required `player.on_ground` to be True to register as pressed. Because the
button sits slightly above the shelf tile, `on_ground` flickered True/False each frame
as the physics resolved, making doors flash open and closed. Removed the `on_ground`
requirement — overlapping the button rect is sufficient.

**`button.py` — Buttons were momentary (doors closed when player stepped off)**
`update_state()` set `self.pressed = pressed` directly each frame, so the button
turned off the moment the player left. Changed to a latch pattern: once `pressed`
is set `True` it never goes back to `False`.

**`level1.py` — Pressure plates too narrow and positioned inside shelf tile**
Original buttons were 40px wide at y=472, placing them partially inside the shelf
tile (surface y=480). Players needed pixel-perfect positioning to activate them.
Fixed: buttons widened to 80px, repositioned to y=468 (flush on shelf surface).

### Features Added

**Level 2** — a new level with a 3-button puzzle, more vertical platforming, and
hazards placed on mid-route platforms rather than just the floor. Both doors require
two buttons each (one cross-side button plus a shared center button), so players
must coordinate more carefully.

**Level progression system** — `game.py` now has a `LEVEL_LOADERS` list and a
`current_level` index. Winning a level shows an **N = Next Level** prompt. Adding
future levels requires only one new file and one line in `LEVEL_LOADERS`.

**Two-button door support** — `door.py` gained an optional `required_button_id_2`
field so a door can require two buttons to be latched before it opens.

**Level indicator in HUD** — the bottom-center of the screen shows "Level 1" or
"Level 2" during play.

---

## Architecture

No structural changes were made to the original class hierarchy or file layout:

```
fireboy_watergirl/
    main.py          Entry point
    settings.py      All constants (screen, physics, colors, game states)
    game.py          Game class: state machine, main loop, all collision logic
    entities/
        player.py    Player physics and input (shared for both characters)
        tile.py      Solid platform/wall sprite
        hazard.py    HazardPool sprite (fire / water / acid)
        button.py    PressurePlate sprite
        door.py      ExitDoor sprite
    levels/
        level1.py    Level 1 data and load_level() factory
        level2.py    Level 2 data and load_level() factory (added in Phase 2)
```

---

## Challenges Encountered

**Sub-pixel physics** was the trickiest bug. The symptom (can't jump) pointed to
`on_ground` never being set, which pointed to `resolve_y` never detecting a
collision, which turned out to be because `int(0.6) == 0` meant the player never
actually moved into the tile. The fix required understanding how float velocities
interact with integer pixel positions.

**Input event vs. polling** is a subtle distinction in Pygame. `get_pressed()` is
correct for movement (held continuously) but wrong for one-shot actions like
starting a game or returning to menu. The original code used `get_pressed()` for
both, causing screens to be skipped instantly.

**Button coordinate math** — getting buttons to sit visually on top of a tile while
also reliably triggering required careful pixel arithmetic. Buttons need their bottom
edge to equal the tile's top edge (button_y = tile_y - button_h), and removing the
`on_ground` requirement from the collision check was needed to stop the flickering.

**Python 3.14 compatibility** — pygame 2.6.1 fails to build from source on Python
3.14 because `distutils` was removed. Required downgrading to Python 3.11 to run
the project.

**Level design iteration** — Level 2 required several layout adjustments after
playtesting: the mid-low platforms needed to move down (y=360 → y=400) to give
enough vertical clearance to jump onto them, and duplicate hazard entries appeared
after that move because the old y-positions weren't fully removed.

---

## Prompt Log

**AI model used:** Claude Sonnet 4.6 via claude.ai

### Prompts that shaped the work


1. *"In level one, the doors don't work with the buttons."*
   — Led to identifying the `on_ground` flickering bug in `_check_buttons()` and
   removing that guard entirely.

2. *"The buttons need to stay 'on' even if the player gets off of it."*
   — Led to the latch fix in `button.py`'s `update_state()` method.

3. *"Create a second level."*
   — Followed by questions about difficulty, mechanics, and button behavior.
   Claude built Level 2 with the 3-button puzzle, updated `door.py` for two-button
   requirements, and added the level progression system to `game.py`. Fixed bugs that also came with this level afterwards. 

4. *"There isn't enough space for the players to jump to the places where there is
   fire and where there is water. That row needs to be moved down a bit."*
   — Led to moving the mid-low platforms from y=360 to y=400 and their hazards
   from y=340 to y=380.

5. *"There's double water/fire now since I moved it down. How do I fix it?"*
   — Claude identified the duplicate hazard entries left over from the old y=340
   positions and told me to delete those two lines.

