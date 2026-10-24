
import os
import random
import pygame

from settings import WIDTH, HEIGHT, ASSET_DIR


class SpaceBackdrop:
    def __init__(self, gif="space.gif", star_count=150):
        self.frames = []      
        self.i = 0
        self.t = 0.0
        self._load_gif(gif)
        if not self.frames:
            self.stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT),
                           random.uniform(0.4, 1.0)] for _ in range(star_count)]

    def _load_gif(self, gif):
        path = os.path.join(ASSET_DIR, "images", gif)
        if not os.path.exists(path):
            return
        try:
            from PIL import Image, ImageSequence
            im = Image.open(path)
            for frame in ImageSequence.Iterator(im):
                rgba = frame.convert("RGBA")
                surf = pygame.image.fromstring(rgba.tobytes(), rgba.size, "RGBA").convert_alpha()
                self.frames.append([self._cover(surf), max(20, frame.info.get("duration", 80))])
        except Exception:
            self.frames = []

    def _cover(self, surf):
        sw, sh = surf.get_size()
        scale = max(WIDTH / sw, HEIGHT / sh)
        return pygame.transform.smoothscale(surf, (round(sw * scale), round(sh * scale)))

    def update(self, dt):
        if self.frames:
            self.t += dt * 1000
            while self.t >= self.frames[self.i][1]:
                self.t -= self.frames[self.i][1]
                self.i = (self.i + 1) % len(self.frames)
        else:
            for s in self.stars:
                s[1] += (10 + 40 * s[2]) * dt       # drift down, parallax by brightness
                if s[1] > HEIGHT:
                    s[0], s[1], s[2] = random.randint(0, WIDTH), 0, random.uniform(0.4, 1.0)

    def draw(self, surf):
        surf.fill((8, 8, 16))
        if self.frames:
            img = self.frames[self.i][0]
            surf.blit(img, img.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        else:
            for x, y, b in self.stars:
                c = int(120 + 135 * b)
                pygame.draw.circle(surf, (c, c, min(255, c + 30)),
                                   (int(x), int(y)), 1 if b < 0.7 else 2)
