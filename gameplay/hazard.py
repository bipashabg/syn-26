import pygame

from engine import assets

WARN   = (240, 180, 40)
DANGER = (226, 60, 60)
SAFE   = (95, 208, 255)


class MemoryTide:
    def __init__(self, interval=11.0, warn=3.0, duration=4.0, safe_zones=None):
        self.interval = interval
        self.warn = warn
        self.duration = duration
        self.safe_zones = list(safe_zones) if safe_zones else []
        self.t = 0.0
        self.phase = "idle"
        self._flash = 0.0

    def set_safe_zones(self, zones):
        self.safe_zones = list(zones)

    def update(self, dt):
        self.t += dt
        if self.phase == "idle" and self.t >= self.interval:
            self.phase, self.t = "warning", 0.0
        elif self.phase == "warning" and self.t >= self.warn:
            self.phase, self.t = "active", 0.0
        elif self.phase == "active" and self.t >= self.duration:
            self.phase, self.t = "idle", 0.0
        self._flash = (self._flash + dt) % 0.6

    @property
    def active(self):
        return self.phase == "active"

    @property
    def warning(self):
        return self.phase == "warning"

    def is_safe(self, rect):
        return any(rect.colliderect(z) for z in self.safe_zones)

    def hitting(self, player):
        return self.active and not self.is_safe(player.rect)

    def draw(self, surf, cam):
        for z in self.safe_zones:
            pygame.draw.rect(surf, SAFE, cam.apply(z), 2)

        if self.warning:
            if self._flash < 0.3:
                pygame.draw.rect(surf, WARN, surf.get_rect(), 6)
            msg = assets.font(18, "pixel.ttf").render("MEMORY TIDE INCOMING", True, WARN)
            surf.blit(msg, (surf.get_width() // 2 - msg.get_width() // 2, 54))
        elif self.active:
            overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            overlay.fill((*DANGER, 70))
            surf.blit(overlay, (0, 0))
            pygame.draw.rect(surf, DANGER, surf.get_rect(), 8)
            msg = assets.font(18, "pixel.ttf").render("TIDE — GET TO COVER", True, DANGER)
            surf.blit(msg, (surf.get_width() // 2 - msg.get_width() // 2, 54))