"""StageScene — the reusable playable stage. Each stage file hands it a config
dict; this class runs the loop (explore, stealth, investigate/collect, exit).

config keys:
  room             CSV filename in data/rooms/
  spawn            (x, y) player start, pixels
  objective        str shown in the HUD
  time             countdown seconds (default 600)
  entity_speed     patrol speed (default 70)
  patrols          list of waypoint-lists, one per entity
  interactables    list of Interactable objects
  intro            dialogue JSON filename to play on entry (optional)
  next             callable(game) to advance to the next stage (optional)
  fragments_needed int; reconstruction triggers once collected (default 0)
  reconstruction   dict: {fragments, correct, true_memory, false_memory}

Terminal interactables (kind="terminal") are HELD with E to investigate: a
progress bar fills over the terminal's investigate_time, and while it fills the
noise lures every enemy toward it. On completion the clue (payload) plays, then
`next` fires.
"""
import os
import pygame

from engine.scene import Scene
from engine.camera import Camera
from engine.tilemap import TileMap
from gameplay.player import Player
from gameplay.enemy import StealthEntity
from gameplay.dialogue import Dialogue
from gameplay.reconstruction import Reconstruction
from gameplay import hud
from gameplay.dilation import DilationClock
from settings import WIDTH, HEIGHT, COLORS, DATA_DIR, DETECT_RATE, DETECT_DECAY


class StageScene(Scene):
    def __init__(self, game, config):
        super().__init__(game)
        self.cfg = config
        self.map = TileMap(
            os.path.join(DATA_DIR, "rooms", config["room"]),
            tile_sprites=config.get("tile_sprites"),
        )
        self.spawn = tuple(config["spawn"])
        self.player = Player(*self.spawn)
        self.cam = Camera(WIDTH, HEIGHT)
        enemy_sprite = config.get("enemy_sprite", "enemy.png")

        self.entities = [
            StealthEntity(
                wp,
                config.get("entity_speed", 70),
                sprite=enemy_sprite,
            )
            for wp in config.get("patrols", [])
        ]
        
        self.interactables = list(config.get("interactables", []))
        self.fragments_needed = config.get("fragments_needed", 0)
        self.fragments_got = 0
        self.objective = config.get("objective", "")
        self.clock = DilationClock(config.get("time", 600))
        self.detection = 0.0
        self._near = None
        self._reconstructed = False
        self._intro_shown = False

    def on_enter(self):
        if self.cfg.get("intro") and not self._intro_shown:
            self._intro_shown = True
            path = os.path.join(DATA_DIR, "dialogue", self.cfg["intro"])
            self.game.push_scene(Dialogue.from_file(self.game, path))

    # ---------- interaction ----------
    def handle_event(self, e):
        if (e.type == pygame.KEYDOWN and e.key == pygame.K_e
                and self._near and self._near.kind in ("log", "fragment", "exit")):
            self._interact(self._near)

    def _interact(self, it):
        if it.used:
            return
        if it.kind == "log":
            it.used = True
            self.game.push_scene(Dialogue(self.game, it.payload))
        elif it.kind == "fragment":
            it.used = True
            self.fragments_got += 1
            if self.fragments_got >= self.fragments_needed and not self._reconstructed:
                self._reconstruct()
        elif it.kind == "exit":
            if self.fragments_needed == 0 or self.fragments_got >= self.fragments_needed:
                self._finish()

    def _reconstruct(self):
        self._reconstructed = True
        rc = self.cfg.get("reconstruction")
        if not rc:
            return
        self.game.push_scene(Reconstruction(
            self.game, rc["fragments"], rc["correct"],
            on_true=lambda: self.game.push_scene(Dialogue(self.game, rc["true_memory"])),
            on_false=lambda: self.game.push_scene(Dialogue(self.game, rc["false_memory"])),
        ))

    def _complete_terminal(self, t):
        nxt = self.cfg.get("next")

        def after():
            if nxt:
                nxt(self.game)

        self.game.push_scene(Dialogue(self.game, t.payload or [], on_done=after))

    def _finish(self):
        nxt = self.cfg.get("next")
        if nxt:
            nxt(self.game)

    def _caught(self):
        self.detection = 0.0
        self.player.pos.update(*self.spawn)

    def _update_near(self):
        self._near = None
        for it in self.interactables:
            if not it.used and self.player.rect.colliderect(it.rect.inflate(26, 26)):
                self._near = it
                break

    # ---------- loop ----------
    def update(self, dt):
        self.player.update(dt, self.map)
        self.clock.update(dt)
        self._update_near()

        keys = pygame.key.get_pressed()
        term = self._near if (self._near and self._near.kind == "terminal"
                              and not self._near.used) else None
        investigating = bool(term and keys[pygame.K_e])

        for en in self.entities:
            if investigating:
                en.lure_toward(term.rect.center, dt)   # noise draws them in
            else:
                en.update(dt, self.map)

        if investigating:
            term.progress += dt / term.investigate_time
            if term.progress >= 1.0:
                term.progress = 1.0
                term.used = True
                self._complete_terminal(term)
        else:
            for it in self.interactables:
                if it.kind == "terminal" and not it.used and it.progress > 0:
                    it.progress = max(0.0, it.progress - 0.5 * dt)

        seen = any(en.can_see(self.player, self.map) for en in self.entities)
        self.detection += (DETECT_RATE if seen else -DETECT_DECAY) * dt
        if investigating:
            self.detection += 0.15 * dt   # investigating is noisy
        self.detection = max(0.0, min(1.0, self.detection))
        if self.detection >= 1.0:
            self._caught()

        self.cam.follow(self.player.rect, self.map.pixel_w, self.map.pixel_h)

    def draw(self, surf):
        surf.fill(COLORS["bg"])
        self.map.draw(surf, self.cam)
        for it in self.interactables:
            it.draw(surf, self.cam, it is self._near)
        for en in self.entities:
            en.draw(surf, self.cam)
        self.player.draw(surf, self.cam)

        obj = self.objective
        if self.fragments_needed:
            obj += f"   fragments {self.fragments_got}/{self.fragments_needed}"
        hud.draw_hud(surf, self.detection, obj, self.clock.label)
