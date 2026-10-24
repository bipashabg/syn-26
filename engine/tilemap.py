"""Loads a room from a CSV grid and handles drawing + collision geometry.

Tile codes:  0 = floor, 1 = wall, 2 = cover (hide here while crouching).
Your teammate builds rooms by editing data/rooms/*.csv — no code needed.
"""
import csv
import pygame

from settings import TILE, COLORS


class TileMap:
    def __init__(self, path):
        self.grid = []
        with open(path) as f:
            for row in csv.reader(f):
                if row:
                    self.grid.append([int(c) for c in row])
        self.h = len(self.grid)
        self.w = len(self.grid[0]) if self.h else 0
        self.pixel_w = self.w * TILE
        self.pixel_h = self.h * TILE

        self.walls = []
        self.cover = []
        for y, row in enumerate(self.grid):
            for x, c in enumerate(row):
                r = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
                if c == 1:
                    self.walls.append(r)
                elif c == 2:
                    self.cover.append(r)

    def is_wall_px(self, px, py):
        tx, ty = int(px // TILE), int(py // TILE)
        if 0 <= ty < self.h and 0 <= tx < self.w:
            return self.grid[ty][tx] == 1
        return True

    def in_cover(self, rect):
        return any(rect.colliderect(c) for c in self.cover)

    def draw(self, surf, cam):
        for y, row in enumerate(self.grid):
            for x, c in enumerate(row):
                if c == 1:
                    color = COLORS["wall"]
                elif c == 2:
                    color = COLORS["cover"]
                else:
                    color = COLORS["floor"]
                r = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
                pygame.draw.rect(surf, color, cam.apply(r))
