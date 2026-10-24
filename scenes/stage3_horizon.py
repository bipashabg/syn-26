"""Stage 3 — "Event Horizon" (climax). Recover the shutdown procedure at the
center, then the revelation and the choice.

This subclasses StageScene to add the gravity-well feel: the deeper you go
toward the center, the more real time your dive costs (clock.mind_cost rises).
Swap in a movement drag here too if you have time.
"""
import os
import json
import pygame

from scenes.stage_base import StageScene
from gameplay.interactable import Interactable
from gameplay.dialogue import Dialogue
from settings import DATA_DIR, WIDTH, HEIGHT


class HorizonStage(StageScene):
    def __init__(self, game, config):
        super().__init__(game, config)
        self.center = pygame.Vector2(self.map.pixel_w / 2, self.map.pixel_h / 2)

    def update(self, dt):
        # the closer to the well, the faster facility-time burns
        d = pygame.Vector2(self.player.rect.center).distance_to(self.center)
        self.clock.mind_cost = 1.0 + max(0.0, (300 - d) / 100.0)
        super().update(dt)

    def _finish(self):
        # climax cutscene -> ending, instead of a plain next-stage jump
        with open(os.path.join(DATA_DIR, "dialogue", "climax.json")) as f:
            lines = json.load(f)

        def to_ending():
            from scenes.ending import EndingScene
            self.game.replace_scene(EndingScene(self.game))

        self.game.push_scene(Dialogue(self.game, lines, on_done=to_ending))


def make(game):
    interactables = [
        Interactable(360, 260, "Fragment", "fragment"),
        Interactable(760, 260, "Fragment", "fragment"),
        Interactable(560, 480, "Fragment", "fragment"),
        Interactable(560, 360, "Shutdown procedure", "exit"),    # center of the well
    ]

    cfg = {
        "room": "stage3.csv",
        "spawn": (96, 96),
        "objective": "Reach the core. Recover the shutdown procedure.",
        "time": 480,
        "entity_speed": 95,
        "patrols": [
            [(470, 200), (470, 500)],
        ],
        "interactables": interactables,
        "fragments_needed": 2,
        "reconstruction": {
            "fragments": [
                "Voss, dying, as the horizon collapsed",
                "Your hand on the override",
                "A consciousness pulled into the system",
                "The voice that has guided you since",
            ],
            "correct": [0, 1, 2, 3],
            "true_memory": [
                {"speaker": "MEMORY", "text": "You broke the protocol to pull her in. To keep something of Lena alive inside the machine."},
                {"speaker": "MNEME", "text": "...you remember me now."},
            ],
            "false_memory": [
                {"speaker": "MEMORY", "text": "You broke the protocol for the data. For the discovery."},
                {"speaker": "MNEME", "text": "No. You never cared about the data. Order it again."},
            ],
        },
    }
    game.replace_scene(HorizonStage(game, cfg))
