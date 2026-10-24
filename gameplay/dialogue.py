"""Dialogue / cutscene overlay. The single most important content system —
a story game lives or dies on it. Transparent, so the room shows behind it.

Lines are a list of dicts: {"speaker": str, "text": str, "portrait": str?}.
Your teammate writes these as JSON in data/dialogue/ — advance with Enter.
"""
import json
import pygame

from engine.scene import Scene
from engine import assets
from settings import WIDTH, HEIGHT, COLORS


class Dialogue(Scene):
    transparent = True

    def __init__(self, game, lines, on_done=None):
        super().__init__(game)
        self.lines = lines
        self.idx = 0
        self.on_done = on_done

    @classmethod
    def from_file(cls, game, path, on_done=None):
        with open(path) as f:
            return cls(game, json.load(f), on_done)

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN and e.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
            self.idx += 1
            if self.idx >= len(self.lines):
                self.game.pop_scene()
                if self.on_done:
                    self.on_done()

    def draw(self, surf):
        if self.idx >= len(self.lines):
            return
        line = self.lines[self.idx]
        box = pygame.Rect(40, HEIGHT - 170, WIDTH - 80, 130)
        pygame.draw.rect(surf, COLORS["box"], box, border_radius=10)
        pygame.draw.rect(surf, COLORS["box_border"], box, 2, border_radius=10)

        speaker = assets.font(20).render(line.get("speaker", ""), True, COLORS["accent"])
        surf.blit(speaker, (box.x + 18, box.y + 14))
        self._wrapped(surf, line.get("text", ""), box.x + 18, box.y + 48,
                      box.width - 36, assets.font(19))
        hint = assets.font(14).render("Enter ▸", True, COLORS["muted"])
        surf.blit(hint, (box.right - 72, box.bottom - 26))

    def _wrapped(self, surf, text, x, y, w, font):
        line, yy = "", y
        for word in text.split():
            test = (line + " " + word).strip()
            if font.size(test)[0] > w and line:
                surf.blit(font.render(line, True, COLORS["text"]), (x, yy))
                yy += 26
                line = word
            else:
                line = test
        if line:
            surf.blit(font.render(line, True, COLORS["text"]), (x, yy))
