"""Interactable — anything you walk up to and press E on.

kind:
  "log"      -> payload is a list of dialogue lines to show
  "fragment" -> counts toward a memory reconstruction
  "exit"     -> leaves the stage (once fragments are collected)
"""
import pygame

from engine import assets
from settings import COLORS


class Interactable:
    def __init__(self, x, y, label, kind, payload=None):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.label = label
        self.kind = kind
        self.payload = payload
        self.used = False

    def draw(self, surf, cam, near):
        if self.used:
            col = COLORS["used"]
        elif self.kind == "fragment":
            col = COLORS["fragment"]
        elif self.kind == "exit":
            col = COLORS["accent"]
        else:
            col = COLORS["log"]
        r = cam.apply(self.rect)
        pygame.draw.rect(surf, col, r, border_radius=6)
        if near and not self.used:
            tag = assets.font(16).render("E", True, (255, 255, 255))
            surf.blit(tag, (r.centerx - tag.get_width() // 2, r.top - 22))
