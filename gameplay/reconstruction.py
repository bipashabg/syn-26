import math
import random
import pygame

from engine.scene import Scene
from engine import assets
from settings import WIDTH, HEIGHT

UI_FONT = "pixel.ttf"
PANEL  = (13, 16, 34)
FRAME  = (95, 208, 255)
VIOLET = (122, 92, 255)
GREEN  = (93, 202, 165)
RED    = (226, 75, 74)
TEXT   = (230, 240, 255)
MUTED  = (130, 145, 180)

CARD_W = 820
CARD_H = 46
GAP = 10
X = (WIDTH - CARD_W) // 2
SEQ_Y = 110


class Reconstruction(Scene):
    transparent = True

    def __init__(self, game, fragments, correct_order, on_true, on_false=None):
        super().__init__(game)
        self.fragments = fragments
        self.correct = list(correct_order)
        self.n = len(self.correct)
        self.on_true = on_true
        self.on_false = on_false or on_true
        self.sequence = []  
        self.cards = [{"i": i, "text": t, "pos": pygame.Vector2(X, self._pool_y(i))}
                      for i, t in enumerate(fragments)]
        self.state = "input"         
        self.result_t = 0.0
        self.pulse = 0.0
        self._done = False

    def _pool_base(self):
        return SEQ_Y + self.n * (CARD_H + GAP) + 54

    def _pool_y(self, idx, pool=None):
        pool = pool if pool is not None else list(range(len(self.fragments)))
        q = pool.index(idx) if idx in pool else 0
        return self._pool_base() + q * (CARD_H + GAP)

    def _target(self, idx):
        if idx in self.sequence:
            p = self.sequence.index(idx)
            return pygame.Vector2(X, SEQ_Y + p * (CARD_H + GAP))
        pool = [i for i in range(len(self.fragments)) if i not in self.sequence]
        return pygame.Vector2(X, self._pool_base() + pool.index(idx) * (CARD_H + GAP))

    def handle_event(self, e):
        if self.state != "input":
            return
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for c in self.cards:
                if pygame.Rect(int(c["pos"].x), int(c["pos"].y), CARD_W, CARD_H).collidepoint(e.pos):
                    self._toggle(c["i"])
                    break
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_BACKSPACE and self.sequence:
                self.sequence.pop()
            elif pygame.K_1 <= e.key <= pygame.K_9:
                self._toggle(e.key - pygame.K_1, place_only=True)

    def _toggle(self, idx, place_only=False):
        if idx >= len(self.fragments):
            return
        if idx in self.sequence:
            if not place_only:
                self.sequence.remove(idx)
        elif len(self.sequence) < self.n:
            self.sequence.append(idx)

    def update(self, dt):
        self.pulse += dt
        for c in self.cards:
            c["pos"] += (self._target(c["i"]) - c["pos"]) * min(1.0, 14 * dt)   # snappy lerp

        if self.state == "input" and len(self.sequence) == self.n:
            self.state = "correct" if self.sequence == self.correct else "wrong"
            self.result_t = 0.0
        elif self.state in ("correct", "wrong"):
            self.result_t += dt
            if self.result_t > 1.4 and not self._done:
                self._done = True
                self.game.pop_scene()
                (self.on_true if self.state == "correct" else self.on_false)()

    def draw(self, surf):
        veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        veil.fill((6, 8, 16, 205))
        surf.blit(veil, (0, 0))

        surf.blit(assets.font(24, UI_FONT).render("RECONSTRUCT THE MEMORY", True, FRAME), (X, 36))
        surf.blit(assets.font(12, UI_FONT).render(
            "Click a fragment to slot it · click it again to pull it back", True, MUTED), (X, 70))

        glow = 140 + int(80 * (0.5 + 0.5 * math.sin(self.pulse * 4)))
        for p in range(len(self.sequence), self.n):
            r = pygame.Rect(X, SEQ_Y + p * (CARD_H + GAP), CARD_W, CARD_H)
            pygame.draw.rect(surf, (glow // 4, glow // 3, glow // 2), r, 1)
            num = assets.font(16, UI_FONT).render(str(p + 1), True, (glow // 2, glow, glow))
            surf.blit(num, (r.x + 14, r.centery - num.get_height() // 2))

        shake = 0
        if self.state == "wrong" and self.result_t < 1.0:
            shake = int(6 * math.sin(self.result_t * 40))

        for c in self.cards:
            placed = c["i"] in self.sequence
            r = pygame.Rect(int(c["pos"].x) + (shake if placed else 0), int(c["pos"].y), CARD_W, CARD_H)
            if self.state == "correct" and placed:
                border, badge = GREEN, GREEN
            elif self.state == "wrong" and placed:
                border, badge = RED, RED
            else:
                border, badge = (FRAME if placed else VIOLET), (FRAME if placed else VIOLET)
            pygame.draw.rect(surf, PANEL, r)
            pygame.draw.rect(surf, border, r, 2)
            if placed:
                p = self.sequence.index(c["i"])
                pygame.draw.rect(surf, badge, pygame.Rect(r.x, r.y, 34, CARD_H))
                bn = assets.font(18, UI_FONT).render(str(p + 1), True, PANEL)
                surf.blit(bn, (r.x + 17 - bn.get_width() // 2, r.centery - bn.get_height() // 2))
            txt = assets.font(14, UI_FONT).render(c["text"], True, TEXT)
            surf.blit(txt, (r.x + 48, r.centery - txt.get_height() // 2))

        if self.state == "correct":
            self._banner(surf, "MEMORY RESTORED", GREEN)
        elif self.state == "wrong":
            self._banner(surf, "SEQUENCE REJECTED", RED)
            if self.result_t < 0.8:
                for _ in range(5):
                    gy = random.randint(SEQ_Y, self._pool_base())
                    pygame.draw.line(surf, RED, (X, gy), (X + CARD_W, gy), 1)

    def _banner(self, surf, text, color):
        img = assets.font(26, UI_FONT).render(text, True, color)
        surf.blit(img, (WIDTH // 2 - img.get_width() // 2, HEIGHT - 70))