"""Stage 2 — "Corruption." Tighter space, two patrols. Reveal: Arin overrode
the safety protocol on purpose — and it was about Lena Voss.

Loads its reconstruction content from data/anomalies.json to show the
data-driven path (your teammate can edit the text without touching code).
"""
import os
import json

from scenes.stage_base import StageScene
from gameplay.interactable import Interactable
from settings import ASSET_DIR, DATA_DIR


def _anomaly(key):
    with open(os.path.join(DATA_DIR, "anomalies.json")) as f:
        return json.load(f)[key]


def make(game):
    def go_next(g):
        from scenes.stage3_horizon import make as make3
        from scenes.loading import LoadingScene

        transition_image = os.path.join(
            ASSET_DIR,
            "images",
            "transitions",
            "stage2_to_stage3_transition.jpg",
        )

        g.replace_scene(
            LoadingScene(
                g,
                duration=4.0,
                on_done=lambda: make3(g),
                background_path=transition_image,
                title="THE CORE MEMORY",
                subtitle="Reconstructing the final memory...",
            )
        )

    interactables = [
        Interactable(
            400, 150, "Archive log", "log",
            [
                {
                    "speaker": "ARCHIVE LOG 07",
                    "text": "Override requires two keys. Only one was turned. Mine."
                }
            ],
            sprite="stage2/tidal_log.png",
            size=(44, 44),
        ),

        Interactable(
            840, 230, "Memory fragment", "fragment",
            sprite="stage2/tidal_fragment.png",
            size=(36, 36),
        ),

        Interactable(
            560, 560, "Memory fragment", "fragment",
            sprite="stage2/tidal_fragment.png",
            size=(36, 36),
        ),

        Interactable(
            230, 560, "Memory fragment", "fragment",
            sprite="stage2/tidal_fragment.png",
            size=(36, 36),
        ),

        Interactable(
            980, 520, "Archive exit", "exit",
            sprite="stage2/tidal_exit.png",
            size=(44, 48),
        ),
    ]

    cfg = {
        "room": "stage2.csv",
        "spawn": (96, 96),
        "objective": "Find all three fragments. Two Watchers now.",
        "time": 540,
        "entity_speed": 85,
        "patrols": [
            [(150, 400), (1000, 400)],
            [(760, 520), (300, 520)],
        ],
        "interactables": interactables,
        "fragments_needed": 3,
        "reconstruction": _anomaly("stage2"),
        "next": go_next,
        "tile_sprites": {
            0: "stage2/tidal_floor.jpg",
            1: "stage2/tidal_wall.jpg",
            2: "stage2/tidal_cover.jpg",
        },

        "enemy_sprite": "stage2/tidal_watcher.png",
    }
    game.replace_scene(StageScene(game, cfg))
