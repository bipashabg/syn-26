"""Stage 1 — "Static." Stealth tutorial: one patrolling Watcher, two fragments,
one log. Reveal: a scratched-out second figure in a memory.
"""
from scenes.stage_base import StageScene
from gameplay.interactable import Interactable
import os
from settings import ASSET_DIR


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
        Interactable(230, 150, "Log", "log", [
            {"speaker": "LOG 01", "text": "Signal acquired 0.3 AU from the horizon. Resonance climbing. Voss flagged the safety margin."},
            {"speaker": "MNEME", "text": "I remember this room. You logged it yourself, Arin. Keep looking."},
        ]),
        Interactable(620, 470, "Fragment", "fragment"),
        Interactable(900, 150, "Fragment", "fragment"),
        Interactable(470, 560, "Exit", "exit"),
    ]

    cfg = {
        "room": "stage1.csv",
        "spawn": (96, 96),
        "objective": "Collect the fragments. Stay out of the Watcher's sight.",
        "time": 600,
        "entity_speed": 70,
        "patrols": [
            [(130, 360), (1020, 360)],   # horizontal sweep across a clear lane
        ],
        "interactables": interactables,
        "fragments_needed": 2,
        "reconstruction": {
            "fragments": [
                "A console, your hands steady",
                "A figure beside you, face scratched out",
                "An alarm you silenced",
            ],
            "correct": [0, 1, 2],
            "true_memory": [
                {"speaker": "MEMORY", "text": "You were not alone at the console. Someone stood beside you — the memory refuses to show the face."},
                {"speaker": "MNEME", "text": "...keep going. You are not ready for that one yet."},
            ],
            "false_memory": [
                {"speaker": "MEMORY", "text": "You worked alone that night. Nothing was wrong."},
                {"speaker": "MNEME", "text": "That is the version you prefer. It is a lie. Try again."},
            ],
        },
        "next": go_next,
    }
    game.replace_scene(StageScene(game, cfg))
