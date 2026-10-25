"""Final choice, cinematic ending, and reset loop."""

import os
import pygame

from engine.scene import Scene
from engine import assets
from settings import ASSET_DIR, DATA_DIR, WIDTH, HEIGHT, COLORS

END_MUSIC = "3_cornfield_chase.ogg"
MUSIC_START_TIME = 31.0  # seconds into the track to start playing
FALLBACK_DURATION = 58.0  # seconds to wait before auto-closing the ending dialogue

class EndingScene(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.mode = "choice"
        self.background_cache = {}

        # Clickable choice cards.
        self.truth_rect = pygame.Rect(55, 330, 395, 155)
        self.reset_rect = pygame.Rect(510, 330, 395, 155)

        self.overlay = pygame.Surface(
            (WIDTH, HEIGHT), pygame.SRCALPHA
        )

    def _image(self, name):
        if name not in self.background_cache:
            path = os.path.join(ASSET_DIR, "images", name)

            try:
                image = pygame.image.load(path).convert()
                image = pygame.transform.smoothscale(
                    image, (WIDTH, HEIGHT)
                )
                self.background_cache[name] = image

            except (pygame.error, OSError) as exc:
                print(f"Could not load {name}: {exc}")
                self.background_cache[name] = None

        return self.background_cache[name]

    def _draw_background(self, surf, name, darkness=145):
        image = self._image(name)

        if image is None:
            surf.fill((4, 7, 18))
        else:
            surf.blit(image, (0, 0))

        self.overlay.fill((3, 6, 18, darkness))
        surf.blit(self.overlay, (0, 0))

    def _center_text(self, surf, text, size, y, color):
        rendered = assets.font(size).render(
            text, True, color
        )
        surf.blit(
            rendered,
            (WIDTH // 2 - rendered.get_width() // 2, y),
        )

    def _draw_card(self, surf, rect, title, descriptions, accent):
        # Translucent box.
        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        panel.fill((4, 12, 27, 225))
        surf.blit(panel, rect.topleft)

        # Colored outline.
        pygame.draw.rect(
            surf, accent, rect, width=2, border_radius=12
        )

        heading = assets.font(21).render(
            title, True, accent
        )
        surf.blit(
            heading,
            (
                rect.centerx - heading.get_width() // 2,
                rect.y + 24,
            ),
        )

        y = rect.y + 70

        for line in descriptions:
            rendered = assets.font(16).render(
                line, True, COLORS["text"]
            )
            surf.blit(
                rendered,
                (
                    rect.centerx - rendered.get_width() // 2,
                    y,
                ),
            )
            y += 26

    def _draw_choice(self, surf):
        self._draw_background(
            surf, "ending/choice_bg.png", darkness=95
        )

        self._center_text(
            surf, "YOUR LAST CHOICE", 38, 65,
            COLORS["text"]
        )

        self._center_text(
            surf,
            "The shutdown code is in your hands.",
            20, 125, COLORS["text"]
        )

        self._draw_card(
            surf,
            self.truth_rect,
            "T - TRANSMIT THE TRUTH",
            [
                "Send the shutdown sequence.",
                "Save the living. Let Mira rest.",
                "Press T or click here",
            ],
            (80, 220, 245),
        )

        self._draw_card(
            surf,
            self.reset_rect,
            "R - RESET THE LOOP",
            [
                "Erase this memory.",
                "Wake again. Repeat the nightmare.",
                "Press R or click here",
            ],
            (180, 135, 255),
        )

    def _start_truth_ending(self):
        from gameplay.dialogue import Dialogue

        pygame.mixer.music.stop()
        
        music_path = os.path.join(
            ASSET_DIR, "audio", END_MUSIC
        )
        
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.45)
            pygame.mixer.music.play(
                start=MUSIC_START_TIME,
                fade_ms=1500,
            )
        except pygame.error as exc:
            print(f"Could not play ending music: {exc}")

        
        path = os.path.join(
            DATA_DIR, "dialogue", "ending_truth.json"
        )

        self.game.push_scene(
            Dialogue.from_file(
                self.game,
                path,
                on_done=self._truth_ending_finished,
                timed=True,
                fallback_duration=FALLBACK_DURATION,
            )
        )

    def _truth_ending_finished(self):
        # Dialogue automatically closes before this callback runs.
        self.mode = "end"

    def _restart(self):
        pygame.mixer.music.stop()

        from scenes.title import TitleScene
        self.game.replace_scene(TitleScene(self.game))

    def handle_event(self, event):
        if self.mode == "choice":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    self._start_truth_ending()
                elif event.key == pygame.K_r:
                    self.mode = "reset"
                elif event.key == pygame.K_ESCAPE:
                    self.game.quit()

            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):
                if self.truth_rect.collidepoint(event.pos):
                    self._start_truth_ending()
                elif self.reset_rect.collidepoint(event.pos):
                    self.mode = "reset"

            return

        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            self.game.quit()

        elif self.mode == "reset":
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._restart()
            elif event.key == pygame.K_q:
                self.game.quit()

        elif self.mode == "end":
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._restart()

    def draw(self, surf):
        if self.mode == "choice":
            self._draw_choice(surf)

        elif self.mode == "reset":
            self._draw_background(
                surf, "ending/the_end.png", darkness=95
            )
            self._center_text(
                surf, "GAME OVER", 48, 150,
                (245, 100, 115)
            )
            self._center_text(
                surf, "MEMORY LOOP REINITIALIZED",
                23, 230, COLORS["text"]
            )
            self._center_text(
                surf,
                "Arin wakes again. The warning will return.",
                18, 285, COLORS["muted"]
            )
            self._center_text(
                surf, "[ENTER] RESTART", 22, 390,
                COLORS["accent"]
            )
            self._center_text(
                surf, "[Q] QUIT", 20, 440,
                COLORS["text"]
            )

        elif self.mode == "end":
            self._draw_background(
                surf, "ending/the_end.png", darkness=125
            )
            # self._center_text(
            #     surf, "THE END", 55, 175,
            #     COLORS["accent"]
            # )
            self._center_text(
                surf, "MINDTRACE: THE LAST RECALL",
                22, 260, COLORS["text"]
            )
            self._center_text(
                surf,
                "THE SIGNAL IS SILENT. THE CATASTROPHE IS AVERTED.",
                16, 320, COLORS["text"]
            )
            self._center_text(
                surf, "PRESS ENTER TO RETURN TO TITLE",
                16, 500, COLORS["text"]
            )