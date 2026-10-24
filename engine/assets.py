"""Asset loading with caching + safe fallbacks.

Nothing crashes if an asset is missing — fonts fall back to a system font and
images to a magenta placeholder — so the game runs before any art exists.
Drop real files into assets/ and swap the placeholder calls when ready.
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


def image(rel_path, size=None):
    key = (rel_path, size)
    if key not in _images:
        full = os.path.join(ASSET_DIR, "images", rel_path)
        try:
            img = pygame.image.load(full).convert_alpha()
            if size:
                img = pygame.transform.smoothscale(img, size)
        except Exception:
            img = pygame.Surface(size or (32, 32), pygame.SRCALPHA)
            img.fill((255, 0, 255, 180))  # obvious "missing art" marker
        _images[key] = img
    return _images[key]
