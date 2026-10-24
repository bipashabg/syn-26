import os
import json

from scenes.stage_base import StageScene
from gameplay.interactable import Interactable
from settings import ASSET_DIR, DATA_DIR


def _dialogue(name):
    with open(os.path.join(DATA_DIR, "dialogue", name)) as f:
        return json.load(f)


def make(game):
    def go_next(g):
        from scenes.stage2_corruption import make as make2
        from scenes.loading import LoadingScene

        transition_image = os.path.join(
            ASSET_DIR,
            "images",
            "transitions",
            "stage1_to_stage2_transition.jpg",
        )

        g.replace_scene(
            LoadingScene(
                g,
                duration=4.0,
                on_done=lambda: make2(g),
                background_path=transition_image,
                title="THE TIDAL ARCHIVE",
                subtitle="Entering the next memory...",
            )
        )

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
