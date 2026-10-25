"""Prologue — "Seven Years." Plays the opening cutscene, then drops into Stage 1."""
import os
import pygame

from engine.scene import Scene
from engine import assets
from gameplay.dialogue import Dialogue
from settings import ASSET_DIR, WIDTH, HEIGHT, COLORS, DATA_DIR

# Prologue music configuration
PROLOGUE_MUSIC = "1_no_time_for_caution.ogg"
MUSIC_START = 153.0          # start from the beginning
MUSIC_VOLUME = 0.4         # Volume between 0.0 and 1.0
PROLOGUE_DURATION = 66.0   # Cinematic duration after music starts


class PrologueScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self._started = False

    def on_enter(self):
        if not self._started:
            self._started = True

            dialogue_path = os.path.join(
                DATA_DIR, "dialogue", "prologue.json"
            )

            music_path = os.path.join(
                ASSET_DIR, "audio", PROLOGUE_MUSIC
            )

            self.game.push_scene(
                Dialogue.from_file(
                    self.game,
                    dialogue_path,
                    on_done=self._go,
                    timed=True,
                    music_path=music_path,
                    music_start=MUSIC_START,
                    music_volume=MUSIC_VOLUME,
                    fallback_duration=PROLOGUE_DURATION,
                )
            )

    def _go(self):
        from scenes.loading import LoadingScene
        from scenes.stage1_static import make

        transition_image = os.path.join(
            ASSET_DIR,
            "images",
            "transitions",
            "prologue_to_stage1_transition.jpg",
        )

        self.game.replace_scene(
            LoadingScene(
                self.game,
                duration=4.0,
                on_done=lambda: make(self.game),
                background_path=transition_image,
                title="THE FORGOTTEN STATION",
                subtitle="Entering Arin's reconstructed memories...",
            )
        )

    def draw(self, surf):
        surf.fill(COLORS["bg"])
        t = assets.font(30).render("UNTITLED", True, COLORS["accent"])
        surf.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 20))
