
import pygame

from engine.scene import Scene
from engine import assets
from engine.anim import SpaceBackdrop
from settings import WIDTH, HEIGHT

UI_FONT = "pixel.ttf"
CYAN   = (95, 208, 255)
ACCENT = (122, 92, 255)
TEXT   = (230, 240, 255)
MUTED  = (150, 160, 190)

LINES = [
    "The recovery team receives the shutdown procedure.",
    "They apply it. The restart halts. The catastrophe is stopped.",
    "Arin's brain activity steadies.",
    "",
    "As the neural link closes, one last voice:",
]
FINAL = "MIRA:  \"You can come back now, Arin.\""


class EndingScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.bg = SpaceBackdrop("space.gif")
        self.t = 0.0

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                from scenes.title import TitleScene
                self.game.replace_scene(TitleScene(self.game))
            elif e.key == pygame.K_ESCAPE:
                self.game.quit()

    def update(self, dt):
        self.t += dt
        self.bg.update(dt)

    def draw(self, surf):
        self.bg.draw(surf)
        veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        veil.fill((6, 8, 16, 150))          
        surf.blit(veil, (0, 0))

        cx = WIDTH // 2
        title = assets.font(28, UI_FONT).render("BACK TO REALITY", True, CYAN)
        surf.blit(title, (cx - title.get_width() // 2, 90))

        reveal = int(self.t / 0.9)        
        y = 190
        for i, ln in enumerate(LINES):
            if i > reveal:
                break
            img = assets.font(15, UI_FONT).render(ln, True, TEXT)
            surf.blit(img, (cx - img.get_width() // 2, y))
            y += 32

        if reveal >= len(LINES):
            fimg = assets.font(17, UI_FONT).render(FINAL, True, ACCENT)
            surf.blit(fimg, (cx - fimg.get_width() // 2, y + 20))
            if reveal >= len(LINES) + 1:
                hint = assets.font(12, UI_FONT).render("Enter ▸ title", True, MUTED)
                surf.blit(hint, (cx - hint.get_width() // 2, y + 80))
