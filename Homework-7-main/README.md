# Fireboy & Watergirl (Pygame Clone)

A two-player local co-op puzzle platformer built with Python and Pygame.

## How to Run

```bash
pip install -r requirements.txt
python -m fireboy_watergirl
```

Requires Python 3.8+ and Pygame 2.1+.

## Controls

| Player    | Move Left | Move Right | Jump |
|-----------|-----------|------------|------|
| Fireboy   | ←         | →          | ↑    |
| Watergirl | A         | D          | W    |

**R** — restart the level at any time
**ENTER** — start game / return to menu

## Rules

- **Fireboy** (red) is immune to fire pools but **dies in water**.
- **Watergirl** (blue) is immune to water pools but **dies in fire**.
- **Acid** (green) kills both players.
- Both players must reach their **exit door simultaneously** to win.
  - Fireboy's door is **red** (top-left).
  - Watergirl's door is **blue** (top-right).

## Level 1 Puzzle

The exit doors are locked behind pressure plates on the **opposite** side of the map:
- Fireboy's red door opens when the **right-side button** is pressed (Watergirl's territory).
- Watergirl's blue door opens when the **left-side button** is pressed (Fireboy's territory).

Both players must cross the hazard-filled center, step on each other's button,
and enter their doors **at the same time**.

## Architecture

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
        level1.py    Level 1 data (LEVEL_DATA) and load_level() factory
```

## Extending

- **Add levels**: create `levels/level2.py` with a new `LEVEL_DATA` list and `load_level()`.
- **Gems**: add a `Gem` sprite class and a collection counter in the HUD.
- **Moving platforms**: give `Tile` a velocity and update its `rect` in a custom `update()` method.
- **Sound**: `pygame.mixer.Sound` for jump, death, and win events.
