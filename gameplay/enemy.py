"""StealthEntity — a patrolling corrupted memory ("Watcher").

Patrol path + facing + a vision cone (range/angle) + a line-of-sight raycast.
`can_see()` is what the stage uses to fill the detection meter. `lure_toward()`
pulls it off patrol toward a noise source (e.g. the terminal being investigated).

Draws `assets.sprite("enemy.png")` centred on its hitbox if present, else a
red block. The vision cone is always drawn — it's essential gameplay feedback.
"""
import math
import pygame

from engine.entity import Entity
from engine import assets
from settings import COLORS, VISION_RANGE, VISION_ANGLE


class StealthEntity(Entity):
    def __init__(self, waypoints, speed=70, vision_range=VISION_RANGE,
                 sprite="enemy.png"):
        pts = [pygame.Vector2(p) for p in waypoints]
        super().__init__(pts[0].x, pts[0].y, 30, 30)
        self.waypoints = pts
        self.i = 1 % len(pts)
        self.speed = speed
        self.range = vision_range
        self.half_angle = math.radians(VISION_ANGLE / 2)
        self.facing = pygame.Vector2(1, 0)
        self.sprite_name = sprite

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

    def lure_toward(self, point, dt):
        """Move toward a noise source, overriding patrol for this frame."""
        center = pygame.Vector2(self.rect.center)
        to = pygame.Vector2(point) - center
        if to.length() > 2:
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
        delta = abs(self.facing.angle_to(to))
        delta = min(delta, 360 - delta)
        if math.radians(delta) > self.half_angle:
            return False
        if player.crouching and tilemap.in_cover(player.rect):
            return False
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

        r = cam.apply(self.rect)
        img = assets.sprite(self.sprite_name, (40, 40)) if self.sprite_name else None
        if img is not None:
            surf.blit(img, img.get_rect(center=r.center))
        else:
            pygame.draw.rect(surf, COLORS["entity"], r, border_radius=5)
