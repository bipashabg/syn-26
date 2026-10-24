"""Ending — the moral choice. T: transmit the truth (let go) / R: reset the loop.
Both are cheap branches; wire a second visual here if time allows.
"""
import pygame

from engine.scene import Scene
from engine import assets
from settings import WIDTH, HEIGHT, COLORS


class EndingScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.choice = None

    def handle_event(self, e):
        if e.type != pygame.KEYDOWN:
            return
        if self.choice is None:
            if e.key == pygame.K_t:
                self.choice = "transmit"
            elif e.key == pygame.K_r:
                self.choice = "reset"
        else:
            if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                from scenes.title import TitleScene
                self.game.replace_scene(TitleScene(self.game))
            elif e.key == pygame.K_ESCAPE:
                self.game.quit()

    def draw(self, surf):
        surf.fill(COLORS["bg"])
        cx = WIDTH // 2
        if self.choice is None:
            q = assets.font(24).render("The shutdown code is in your hands.", True, COLORS["text"])
            surf.blit(q, (cx - q.get_width() // 2, 170))
            o1 = assets.font(20).render("[T]  Transmit the truth  —  finish it, and let her go", True, COLORS["accent"])
            o2 = assets.font(20).render("[R]  Reset the loop  —  wake again, remember nothing", True, COLORS["muted"])
            surf.blit(o1, (cx - o1.get_width() // 2, 300))
            surf.blit(o2, (cx - o2.get_width() // 2, 350))
        else:
            if self.choice == "transmit":
                lines = ["You send the code. The facility stabilises.",
                         "MNEME goes quiet. The last of Lena with it.",
                         "Seven years too late, you keep your promise."]
            else:
                lines = ["You let the loop close.",
                         "The alarms begin again. A voice says: wake up, Arin.",
                         "You remember nothing. You never do."]
            y = 200
            for ln in lines:
                r = assets.font(20).render(ln, True, COLORS["text"])
                surf.blit(r, (cx - r.get_width() // 2, y))
                y += 40
            hint = assets.font(15).render("Enter — return to title", True, COLORS["muted"])
            surf.blit(hint, (cx - hint.get_width() // 2, y + 24))
