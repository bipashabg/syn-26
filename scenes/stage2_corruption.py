"""Stage 2 — "Corruption." Tighter space, two patrols. Reveal: Arin overrode
the safety protocol on purpose — and it was about Lena Voss.

Loads its reconstruction content from data/anomalies.json to show the
data-driven path (your teammate can edit the text without touching code).
"""
import os
import json

from scenes.stage_base import StageScene
from gameplay.interactable import Interactable
from settings import DATA_DIR


def _anomaly(key):
    with open(os.path.join(DATA_DIR, "anomalies.json")) as f:
        return json.load(f)[key]


def make(game):
    def go_next(g):
        from scenes.stage3_horizon import make as make3
        make3(g)

    interactables = [
        Interactable(400, 150, "Log", "log", [
            {"speaker": "LOG 07", "text": "Override requires two keys. Only one was turned. Mine."},
        ]),
        Interactable(840, 230, "Fragment", "fragment"),
        Interactable(560, 560, "Fragment", "fragment"),
        Interactable(230, 560, "Fragment", "fragment"),
        Interactable(980, 520, "Exit", "exit"),
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
    }
    game.replace_scene(StageScene(game, cfg))
