# settings.py — all constants for Fireboy & Watergirl clone

# Screen
SCREEN_W = 800
SCREEN_H = 600
TITLE = "Fireboy & Watergirl"
FPS = 60

# Physics
GRAVITY = 0.6
JUMP_STRENGTH = -13
MAX_FALL_SPEED = 18
PLAYER_SPEED = 4

# Tile size (used as mental grid unit during level design; not enforced at runtime)
TILE = 40

# Colors (R, G, B)
BLACK        = (0, 0, 0)
WHITE        = (255, 255, 255)
BG_COLOR     = (30, 30, 40)
FIRE_COLOR   = (220, 80, 20)
WATER_COLOR  = (30, 130, 220)
ACID_COLOR   = (80, 200, 60)
TILE_COLOR   = (90, 80, 70)
BUTTON_OFF   = (180, 160, 140)
BUTTON_ON    = (255, 220, 60)

# Player sizes
PLAYER_W = 28
PLAYER_H = 40

# Element identifiers
FIRE  = "fire"
WATER = "water"
ACID  = "acid"

# Game states
STATE_MENU      = "menu"
STATE_PLAYING   = "playing"
STATE_WIN       = "win"
STATE_GAME_OVER = "game_over"
