"""Ren — the player. Top-down movement with axis-separated wall collision,
plus a crouch that slows you and lets cover tiles hide you from entities.
"""
import pygame

from engine.entity import Entity
from settings import COLORS, PLAYER_SPEED, PLAYER_CROUCH_SPEED


class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 28, 28)
        self.facing = pygame.Vector2(0, 1)
        self.crouching = False

    def _read_input(self):
        keys = pygame.key.get_pressed()
        self.crouching = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        v = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            v.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            v.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            v.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            v.x += 1
        if v.length_squared() > 0:
            v = v.normalize()
            self.facing = v
        return v

    def update(self, dt, tilemap):
        v = self._read_input()
        speed = PLAYER_CROUCH_SPEED if self.crouching else PLAYER_SPEED
        self._move_axis(v.x * speed * dt, 0, tilemap)
        self._move_axis(0, v.y * speed * dt, tilemap)

    def _move_axis(self, dx, dy, tilemap):
        self.pos.x += dx
        self.pos.y += dy
        r = self.rect
        for w in tilemap.walls:
            if r.colliderect(w):
                if dx > 0:
                    r.right = w.left
                elif dx < 0:
                    r.left = w.right
                if dy > 0:
                    r.bottom = w.top
                elif dy < 0:
                    r.top = w.bottom
                self.pos.update(r.x, r.y)

    def draw(self, surf, cam):
        r = cam.apply(self.rect)
        col = COLORS["player_crouch"] if self.crouching else COLORS["player"]
        pygame.draw.rect(surf, col, r, border_radius=7)
        center = pygame.Vector2(r.center)
        pygame.draw.line(surf, (255, 255, 255), center, center + self.facing * 18, 2)
