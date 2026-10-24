"""Dialogue / cutscene overlay — pixel / cyber styled, with a typewriter reveal.

Text types out character by character and ticks a sound (assets/audio/type.wav)
as it goes. First Enter finishes the current line instantly; next Enter advances.
Transparent, so the room shows behind it.

Lines: list of {"speaker", "text", "portrait"?}. Drop assets/fonts/pixel.ttf for
the pixel font (falls back to mono) and assets/audio/type.wav for the tick.
"""
import json
import pygame

from engine.scene import Scene
from engine import assets, audio
from settings import WIDTH, HEIGHT

UI_FONT = "pixel.ttf"
CHARS_PER_SEC = 45          # typewriter speed
TYPE_SOUND = "type.wav"

PANEL  = (13, 16, 34)
FRAME  = (95, 208, 255)
INNER  = (43, 108, 230)
ACCENT = (122, 92, 255)
TEXT   = (230, 240, 255)
MUTED  = (120, 140, 190)


class Dialogue(Scene):
    transparent = True

    def __init__(self, game, lines, on_done=None):
        super().__init__(game)
        self.lines = lines
        self.idx = 0
        self.on_done = on_done
        self.shown = 0.0        # chars revealed so far (float)
        self._played = 0        # how many chars we've ticked for

    @classmethod
    def from_file(cls, game, path, on_done=None):
        with open(path, encoding="utf-8-sig") as f:
            return cls(game, json.load(f), on_done)

    def _text(self):
        if self.idx < len(self.lines):
            return self.lines[self.idx].get("text", "")
        return ""

    def update(self, dt):
        text = self._text()
        if self.shown < len(text):
            self.shown = min(len(text), self.shown + CHARS_PER_SEC * dt)
            n = int(self.shown)
            if n > self._played:
                ch = text[n - 1] if 0 < n <= len(text) else " "
                if ch != " " and n % 2 == 0:
                    audio.play(TYPE_SOUND, 0.5)
                self._played = n

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN and e.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
            text = self._text()
            if self.shown < len(text):
                self.shown = len(text)          # first press: reveal the rest
            else:
                self.idx += 1                   # next press: advance
                self.shown = 0.0
                self._played = 0
                if self.idx >= len(self.lines):
                    self.game.pop_scene()
                    if self.on_done:
                        self.on_done()

    def draw(self, surf):
        if self.idx >= len(self.lines):
            return
        line = self.lines[self.idx]
        box = pygame.Rect(30, HEIGHT - 150, WIDTH - 60, 120)

        pygame.draw.rect(surf, PANEL, box)
        pygame.draw.rect(surf, FRAME, box, 3)
        pygame.draw.rect(surf, INNER, box.inflate(-10, -10), 1)
        for cx, cy in ((box.left, box.top), (box.right - 6, box.top),
                       (box.left, box.bottom - 6), (box.right - 6, box.bottom - 6)):
            pygame.draw.rect(surf, ACCENT, pygame.Rect(cx, cy, 6, 6))

        surf.blit(assets.font(18, UI_FONT).render(line.get("speaker", ""), True, ACCENT),
                  (box.x + 18, box.y + 14))
        shown_text = line.get("text", "")[:int(self.shown)]
        self._wrapped(surf, shown_text, box.x + 18, box.y + 46,
                      box.width - 36, assets.font(15, UI_FONT))
        if self.shown >= len(line.get("text", "")):
            hint = assets.font(12, UI_FONT).render("Enter ▸", True, MUTED)
            surf.blit(hint, (box.right - hint.get_width() - 16, box.bottom - 24))

    def _wrapped(self, surf, text, x, y, w, font):
        line, yy = "", y
        for word in text.split():
            test = (line + " " + word).strip()
            if font.size(test)[0] > w and line:
                surf.blit(font.render(line, True, TEXT), (x, yy))
                yy += font.get_height() + 6
                line = word
            else:
                line = test
        if line:
            surf.blit(font.render(line, True, TEXT), (x, yy))
