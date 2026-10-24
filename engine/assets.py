"""Asset loading with caching + safe fallbacks.

Fonts fall back to a system font. For sprites, use `sprite(name)` — it returns
None when the file is missing so callers can draw a placeholder shape instead,
which means the game runs before any art exists and each sprite can be dropped
in one at a time.
"""
import os
import pygame

from settings import FONT_DIR, ASSET_DIR

_fonts = {}
_images = {}


def font(size, name=None):
    key = (name, size)
    if key not in _fonts:
        path = os.path.join(FONT_DIR, name) if name else None
        try:
            if path and os.path.exists(path):
                _fonts[key] = pygame.font.Font(path, size)
            else:
                _fonts[key] = pygame.font.SysFont("consolas,menlo,monospace", size)
        except Exception:
            _fonts[key] = pygame.font.SysFont(None, size)
    return _fonts[key]


def sprite(name, size=None):
    """Return a Surface for assets/images/<name>, scaled to `size`, or None if
    the file is missing. No magenta placeholder — callers fall back to shapes."""
    if not name:
        return None
    key = ("sprite", name, size)
    if key in _images:
        return _images[key]
    full = os.path.join(ASSET_DIR, "images", name)
    img = None
    if os.path.exists(full):
        try:
            img = pygame.image.load(full).convert_alpha()
            if size:
                img = pygame.transform.smoothscale(img, size)
        except Exception:
            img = None
    _images[key] = img
    return img


def sheet_cell(sheet_name, col, row, cell_w, cell_h,
               size=None, margin=0, spacing=0):
    """Slice one cell out of a uniform-grid spritesheet in assets/images/.
    col/row are 0-based. Use this only if you have the big sheet and not the
    individual PNGs — individual PNGs via sprite() are simpler."""
    sheet = sprite(sheet_name)   # full sheet, unscaled + cached
    if sheet is None:
        return None
    x = margin + col * (cell_w + spacing)
    y = margin + row * (cell_h + spacing)
    try:
        cell = sheet.subsurface(pygame.Rect(x, y, cell_w, cell_h)).copy()
        if size:
            cell = pygame.transform.smoothscale(cell, size)
        return cell
    except Exception:
        return None


def image(rel_path, size=None):
    """Like sprite() but returns a visible magenta placeholder if missing."""
    img = sprite(rel_path, size)
    if img is None:
        img = pygame.Surface(size or (32, 32), pygame.SRCALPHA)
        img.fill((255, 0, 255, 180))
    return img
