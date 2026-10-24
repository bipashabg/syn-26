"""Global constants and theme. Tune gameplay feel here."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSET_DIR = os.path.join(BASE_DIR, "assets")
FONT_DIR = os.path.join(ASSET_DIR, "fonts")

WIDTH, HEIGHT = 960, 600
FPS = 60
TILE = 48

# --- player ---
PLAYER_SPEED = 180          # px/sec
PLAYER_CROUCH_SPEED = 90

# --- stealth ---
VISION_RANGE = 190          # how far an entity can see (px)
VISION_ANGLE = 70           # full cone angle (degrees)
DETECT_RATE = 0.9           # detection meter fill /sec while seen
DETECT_DECAY = 0.6          # detection meter drain /sec while hidden

# Tile codes used in data/rooms/*.csv
# 0 = floor, 1 = wall, 2 = cover (hide here while crouching)
COLORS = {
    "bg":            (14, 14, 20),
    "floor":         (30, 30, 42),
    "wall":          (60, 62, 86),
    "cover":         (26, 44, 50),
    "player":        (126, 230, 180),
    "player_crouch": (90, 170, 140),
    "entity":        (226, 75, 74),
    "cone":          (226, 75, 74, 55),   # RGBA — alpha matters
    "fragment":      (120, 170, 230),
    "log":           (240, 200, 120),
    "used":          (70, 70, 84),
    "accent":        (126, 230, 180),
    "muted":         (120, 120, 140),
    "alert":         (226, 75, 74),
    "text":          (228, 228, 234),
    "box":           (20, 22, 32),
    "box_border":    (70, 74, 100),
}
