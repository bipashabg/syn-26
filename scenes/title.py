"""Title screen. Enter to begin, Esc to quit."""
import pygame
import os

from engine.scene import Scene
from engine import assets
from settings import ASSET_DIR,WIDTH, HEIGHT, COLORS

TITLE_MUSIC = "2_STAY.ogg"
MUSIC_START = 65.0

class TitleScene(Scene):
    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                from scenes.prologue import PrologueScene
                self.game.replace_scene(PrologueScene(self.game))
            elif e.key == pygame.K_ESCAPE:
                self.game.quit()
                
    def on_enter(self):
        music_path = os.path.join(
            ASSET_DIR, "audio", TITLE_MUSIC
        )

        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.35)
            pygame.mixer.music.play(-1,start=MUSIC_START)

        except pygame.error as e:
            print("Could not play title music:", e)
            
    def on_exit(self):
        pygame.mixer.music.stop()

    def draw(self, surf):
        surf.fill(COLORS["bg"])
        title = assets.font(56).render("UNTITLED", True, COLORS["accent"])
        surf.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 90))
        sub = assets.font(18).render("enter the mind. recover the truth.", True, COLORS["muted"])
        surf.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 - 30))
        start = assets.font(20).render("Press Enter to begin", True, COLORS["text"])
        surf.blit(start, (WIDTH // 2 - start.get_width() // 2, HEIGHT // 2 + 50))
