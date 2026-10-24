"""Base entity. `pos` is the top-left corner in world (pixel) coordinates."""
import pygame


class Entity:
    def __init__(self, x, y, w, h):
        self.pos = pygame.Vector2(x, y)
        self.size = (w, h)

    @property
    def rect(self):
        return pygame.Rect(int(self.pos.x), int(self.pos.y), self.size[0], self.size[1])

    def update(self, dt, tilemap):
        pass

    def draw(self, surf, cam):
        pass
