import os
import json

from scenes.stage_base import StageScene
from gameplay.interactable import Interactable
from gameplay.dialogue import Dialogue
from gameplay.reconstruction import Reconstruction
from gameplay.hazard import MemoryTide
from settings import DATA_DIR


def _dialogue(name):
    with open(os.path.join(DATA_DIR, "dialogue", name), encoding="utf-8-sig") as f:
        return json.load(f)


SHUTDOWN = {
    "fragments": [
        "Disable the signal resonator",
        "Vent the stored energy",
        "Isolate the core",
    ],
    "correct": [0, 1, 2],
    "true_memory": [
        {"speaker": "SYSTEM", "text": "Shutdown sequence accepted. Resonance collapsing."},
        {"speaker": "MIRA", "text": "That's it, Arin. You remembered. You can come back now."},
    ],
    "false_memory": [
        {"speaker": "SYSTEM", "text": "Sequence rejected. Instability rising."},
        {"speaker": "MIRA", "text": "No — think. Resonator, then energy, then core. In that order."},
    ],
}


class CoreMemoryStage(StageScene):
    def __init__(self, game, cfg):
        super().__init__(game, cfg)
        # safe zones = the cover tiles already in the room
        self.tide = MemoryTide(interval=11.0, warn=3.0, duration=4.0,
                               safe_zones=self.map.cover)

    def update(self, dt):
        super().update(dt)
        self.tide.update(dt)
        if self.tide.hitting(self.player):   # caught in the open during a wave
            self._caught()

    def draw(self, surf):
        super().draw(surf)
        self.tide.draw(surf, self.cam)

    def _complete_terminal(self, t):
        """Core console done -> play the recording, then the shutdown puzzle."""
        self.game.push_scene(Dialogue(self.game, t.payload or [], on_done=self._start_puzzle))

    def _start_puzzle(self):
        self.game.push_scene(Reconstruction(
            self.game, SHUTDOWN["fragments"], SHUTDOWN["correct"],
            on_true=lambda: self.game.push_scene(
                Dialogue(self.game, SHUTDOWN["true_memory"], on_done=self._to_ending)),
            on_false=lambda: self.game.push_scene(
                Dialogue(self.game, SHUTDOWN["false_memory"], on_done=self._start_puzzle)),
        ))

    def _to_ending(self):
        from scenes.ending import EndingScene
        self.game.replace_scene(EndingScene(self.game))


def make(game):
    console = Interactable(
        554, 362, "Core console", "terminal",      
        payload=_dialogue("stage3_recording.json"),
        sprite="terminal.png", size=(44, 44),
        investigate_time=3.5,
    )
    cfg = {
        "room": "stage3.csv",
        "tiles": {0: "floor3.png", 1: "wall3.png", 2: "cover3.png"},
        "enemy_sprite": "enemy3.png",
        "spawn": (96, 96),
        "objective": "Reach the core console. Time the Tide and the guardian.",
        "time": 480,
        "entity_speed": 55,
        "patrols": [
            [(240, 180), (912, 180), (912, 600), (240, 600)],   # slow loop around the chamber
        ],
        "interactables": [console],
        "intro": "stage3.json",
        "music": "stage3_music.wav",
    }
    game.replace_scene(CoreMemoryStage(game, cfg))