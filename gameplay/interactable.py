"""Interactable — anything you walk up to and act on.

kind:
  "log"      -> payload is a list of dialogue lines; press E to read
  "fragment" -> counts toward a memory reconstruction; press E to take
  "exit"     -> leaves the stage (once any fragments are collected)
  "terminal" -> HOLD E to investigate over `investigate_time` seconds; it
                fills a progress bar and makes noise that lures enemies. On
                completion it plays `payload` (the clue) then advances.

`sprite` is a filename in assets/images/ (e.g. "terminal.png"). If it's missing
or not set, a plain coloured block is drawn instead, so the game still runs.
"""
import pygame

from engine import assets
from settings import COLORS


class Interactable:
    def __init__(self, x, y, label, kind, payload=None,
                 sprite=None, size=(40, 40), investigate_time=3.0):
        self.rect = pygame.Rect(x, y, size[0], size[1])
        self.label = label
        self.kind = kind
        self.payload = payload
        self.sprite_name = sprite
        self.size = size
        self.used = False
        self.investigate_time = investigate_time
        self.progress = 0.0

    def draw(self, surf, cam, near):
        r = cam.apply(self.rect)
        name = self.sprite_name or {"fragment": "fragment.png", "log": "log.png", "exit": "exit.png", "terminal": "terminal.png"}.get(self.kind)
        img = assets.sprite(name, self.size) if name else None
        if img is not None:
            if self.used:
                img = img.copy()
                img.set_alpha(90)
            surf.blit(img, r)
        else:
            if self.used:
                col = COLORS["used"]
            elif self.kind == "fragment":
                col = COLORS["fragment"]
            elif self.kind in ("exit", "terminal"):
                col = COLORS["accent"]
            else:
                col = COLORS["log"]
            pygame.draw.rect(surf, col, r, border_radius=6)

        if self.kind == "terminal" and 0.0 < self.progress < 1.0 and not self.used:
            track = pygame.Rect(r.x, r.top - 10, r.width, 5)
            pygame.draw.rect(surf, (40, 40, 52), track, border_radius=3)
            fill = pygame.Rect(r.x, r.top - 10, int(r.width * self.progress), 5)
            pygame.draw.rect(surf, COLORS["accent"], fill, border_radius=3)

        if near and not self.used:
            tag = assets.font(16).render("E", True, (255, 255, 255))
            surf.blit(tag, (r.centerx - tag.get_width() // 2, r.top - 28))
