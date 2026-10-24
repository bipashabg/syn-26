"""Prologue — "Seven Years." Plays the opening cutscene, then drops into Stage 1."""
import os
import pygame

from engine.scene import Scene
from engine import assets
from gameplay.dialogue import Dialogue
from settings import WIDTH, HEIGHT, COLORS, DATA_DIR


class PrologueScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self._started = False

    def on_enter(self):
        if not self._started:
            self._started = True
            path = os.path.join(DATA_DIR, "dialogue", "prologue.json")
            self.game.push_scene(Dialogue.from_file(self.game, path, on_done=self._go))

    def _go(self):
        from scenes.stage1_static import make
        make(self.game)

    def draw(self, surf):
        surf.fill(COLORS["bg"])
        t = assets.font(30).render("UNTITLED", True, COLORS["accent"])
        surf.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 20))
