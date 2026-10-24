"""Stage 1 — "The Forgotten Station."

A mental reconstruction of the Asterion. One corrupted-memory Watcher patrols.
Reach the research terminal and HOLD E to investigate it — investigating takes
a few seconds and makes noise that pulls the Watcher toward you. The clue:
Arin overrode the safety system himself. Then the station's Tidal Archive opens.
"""
import os
import json

from scenes.stage_base import StageScene
from gameplay.interactable import Interactable
from settings import DATA_DIR


def _dialogue(name):
    with open(os.path.join(DATA_DIR, "dialogue", name)) as f:
        return json.load(f)


def make(game):
    def go_next(g):
        from scenes.stage2_corruption import make as make2
        make2(g)

    interactables = [
        Interactable(
            620, 470, "Research terminal", "terminal",
            payload=_dialogue("stage1_clue.json"),
            sprite="terminal.png",      # drop assets/images/terminal.png to skin it
            size=(44, 44),
            investigate_time=3.0,
        ),
    ]

    cfg = {
        "room": "stage1.csv",
        "spawn": (96, 96),
        "objective": "Reach the research terminal. Hold E to investigate — it makes noise.",
        "time": 600,
                "entity_speed": 55,
        "patrols": [
            [(200, 140), (1000, 140), (1000, 640), (620, 640), (620, 300), (200, 300)],
        ],
        "interactables": interactables,
        "intro": "stage1.json",
        "next": go_next,
    }
    game.replace_scene(StageScene(game, cfg))
