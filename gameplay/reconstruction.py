"""Reconstruction puzzle — the mind mechanic.

You collect scattered fragments, then order them. The correct order reveals the
true memory; a wrong order plays the lie your mind tells itself. Overlay scene;
press number keys to place fragments, Backspace to undo.

Upgrade path (if you have time): replace the ordering with a live rewind/scrub.
"""
import pygame

from engine.scene import Scene
from engine import assets
from settings import WIDTH, HEIGHT, COLORS


class Reconstruction(Scene):
    transparent = True

    def __init__(self, game, fragments, correct_order, on_true, on_false=None):
        super().__init__(game)
        self.fragments = fragments          # list[str]
        self.correct = list(correct_order)  # list[int]
        self.sequence = []
        self.on_true = on_true
        self.on_false = on_false or on_true

    def handle_event(self, e):
        if e.type != pygame.KEYDOWN:
            return
        if e.key == pygame.K_BACKSPACE and self.sequence:
            self.sequence.pop()
        elif pygame.K_1 <= e.key <= pygame.K_9:
            n = e.key - pygame.K_1
            if n < len(self.fragments) and n not in self.sequence:
                self.sequence.append(n)
                if len(self.sequence) == len(self.correct):
                    ok = self.sequence == self.correct
                    self.game.pop_scene()
                    (self.on_true if ok else self.on_false)()

    def draw(self, surf):
        panel = pygame.Rect(80, 70, WIDTH - 160, HEIGHT - 150)
        pygame.draw.rect(surf, COLORS["box"], panel, border_radius=12)
        pygame.draw.rect(surf, COLORS["box_border"], panel, 2, border_radius=12)

        surf.blit(assets.font(24).render("Reconstruct the memory", True, COLORS["accent"]),
                  (panel.x + 22, panel.y + 18))
        surf.blit(assets.font(15).render(
            "Number keys to order the fragments · Backspace to undo",
            True, COLORS["muted"]), (panel.x + 22, panel.y + 52))

        y = panel.y + 96
        for i, frag in enumerate(self.fragments):
            slot = str(self.sequence.index(i) + 1) if i in self.sequence else "·"
            txt = f"[{i + 1}]  ({slot})  {frag}"
            surf.blit(assets.font(19).render(txt, True, COLORS["text"]), (panel.x + 26, y))
            y += 36
