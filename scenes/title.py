import pygame
import os

from engine.scene import Scene
from engine import assets, audio
from settings import ASSET_DIR,WIDTH, HEIGHT, COLORS

TITLE_MUSIC = "2_STAY.ogg"
MUSIC_START = 65.0

def on_enter(self):
    audio.music_play("2_STAY.ogg")      

def on_exit(self):
    audio.music_stop()

class TitleScene(Scene):
    def __init__(self, game):
        super().__init__(game)

        image_path = os.path.join(
            ASSET_DIR,
            "images",
            "title_background.png",
        )

        try:
            image = pygame.image.load(image_path).convert()
            self.background = pygame.transform.smoothscale(
                image, (WIDTH, HEIGHT)
            )
        except (pygame.error, OSError) as exc:
            print("Could not load title background:", exc)
            self.background = None

        # Dark transparent layer for readable menu text
        self.overlay = pygame.Surface(
            (WIDTH, HEIGHT), pygame.SRCALPHA
        )
        self.overlay.fill((3, 7, 18, 145))
    
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
        # Draw the title background.
        if self.background is not None:
            surf.blit(self.background, (0, 0))
        else:
            surf.fill(COLORS["bg"])

        # Darken the image for readable text.
        surf.blit(self.overlay, (0, 0))

        # Main game title.
        title = assets.font(56).render(
            "Welcome to Project Gargantua", True, COLORS["accent"]
        )
        surf.blit(
            title,
            (
                WIDTH // 2 - title.get_width() // 2,
                HEIGHT // 2 - 110,
            ),
        )

        # Subtitle.
        subtitle = assets.font(26).render(
            "THE LAST RECALL", True, COLORS["text"]
        )
        surf.blit(
            subtitle,
            (
                WIDTH // 2 - subtitle.get_width() // 2,
                HEIGHT // 2 - 48,
            ),
        )

        # Tagline.
        tagline = assets.font(17).render(
            "ENTER THE MIND. RECOVER THE TRUTH.",
            True, COLORS["muted"]
        )
        surf.blit(
            tagline,
            (
                WIDTH // 2 - tagline.get_width() // 2,
                HEIGHT // 2 + 18,
            ),
        )

        # Start prompt.
        start = assets.font(20).render(
            "Press Enter to begin", True, COLORS["text"]
        )
        surf.blit(
            start,
            (
                WIDTH // 2 - start.get_width() // 2,
                HEIGHT // 2 + 95,
            ),
        )
