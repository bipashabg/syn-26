"""A follow camera that clamps to the map bounds."""
import pygame


class Camera:
    def __init__(self, view_w, view_h):
        self.view_w = view_w
        self.view_h = view_h
        self.offset = pygame.Vector2(0, 0)

    def follow(self, target_rect, map_w, map_h):
        x = target_rect.centerx - self.view_w / 2
        y = target_rect.centery - self.view_h / 2
        x = max(0, min(x, max(0, map_w - self.view_w)))
        y = max(0, min(y, max(0, map_h - self.view_h)))
        self.offset.update(x, y)

    def apply(self, rect):
        return rect.move(-int(self.offset.x), -int(self.offset.y))

    def apply_point(self, pos):
        return (pos[0] - self.offset.x, pos[1] - self.offset.y)
