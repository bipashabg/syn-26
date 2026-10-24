"""StealthEntity — a patrolling "memory guardian".

This is the meatiest system in the game: a patrol path, a facing vector, a
vision cone (range + angle), and a line-of-sight raycast against walls. If the
player is inside the cone AND there's a clear line AND they aren't crouched in
cover, the entity sees them. `can_see()` is what the stage uses to fill the
detection meter.
"""
import math
import pygame

from engine.entity import Entity
from settings import COLORS, VISION_RANGE, VISION_ANGLE


class StealthEntity(Entity):
    def __init__(self, waypoints, speed=70, vision_range=VISION_RANGE):
        pts = [pygame.Vector2(p) for p in waypoints]
        super().__init__(pts[0].x, pts[0].y, 30, 30)
        self.waypoints = pts
        self.i = 1 % len(pts)
        self.speed = speed
        self.range = vision_range
        self.half_angle = math.radians(VISION_ANGLE / 2)
        self.facing = pygame.Vector2(1, 0)

    def update(self, dt, tilemap):
        if len(self.waypoints) < 2:
            return
        center = pygame.Vector2(self.rect.center)
        target = self.waypoints[self.i]
        to = target - center
        if to.length() < 4:
            self.i = (self.i + 1) % len(self.waypoints)
        else:
            d = to.normalize()
            self.facing = d
            self.pos += d * self.speed * dt

    def can_see(self, player, tilemap):
        ec = pygame.Vector2(self.rect.center)
        pc = pygame.Vector2(player.rect.center)
        to = pc - ec
        dist = to.length()
        if dist > self.range:
            return False
        if dist < 1:
            return True
        # inside the cone?
        delta = abs(self.facing.angle_to(to))
        delta = min(delta, 360 - delta)
        if math.radians(delta) > self.half_angle:
            return False
        # hidden if crouched in cover
        if player.crouching and tilemap.in_cover(player.rect):
            return False
        # clear line of sight?
        steps = max(2, int(dist // 8))
        for s in range(1, steps):
            p = ec + to * (s / steps)
            if tilemap.is_wall_px(p.x, p.y):
                return False
        return True

    def draw(self, surf, cam):
        ec = pygame.Vector2(cam.apply(self.rect).center)
        base = math.atan2(self.facing.y, self.facing.x)
        pts = [ec]
        for k in range(-4, 5):
            a = base + self.half_angle * (k / 4)
            pts.append(ec + pygame.Vector2(math.cos(a), math.sin(a)) * self.range)
        cone = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(cone, COLORS["cone"], pts)
        surf.blit(cone, (0, 0))
        pygame.draw.rect(surf, COLORS["entity"], cam.apply(self.rect), border_radius=5)
