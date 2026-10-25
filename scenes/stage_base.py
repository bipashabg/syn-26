import os
import pygame

from engine.scene import Scene
from engine.camera import Camera
from engine.tilemap import TileMap
from engine import audio
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
            config.get("tiles") or config.get("tile_sprites"),
        )
        self.spawn = tuple(config["spawn"])
        self.player = Player(*self.spawn)
        self.cam = Camera(WIDTH, HEIGHT)
        self.entities = [
            StealthEntity(wp, config.get("entity_speed", 70),
                          sprite=config.get("enemy_sprite", "enemy.png"))
            for wp in config.get("patrols", [])
        ]
        self.interactables = list(config.get("interactables", []))
        self.fragments_needed = config.get("fragments_needed", 0)
        self.fragments_got = 0
        self.objective = config.get("objective", "")
        self.clock = DilationClock(config.get("time", 600))
        self.detection = 0.0
        self._near = None
        self._seen_last = False
        self._alarm_chan = None
        self._reconstructed = False
        self._intro_shown = False

    def on_enter(self):
        if self.cfg.get("music"):
            audio.music_play(self.cfg["music"])
        if self.cfg.get("intro") and not self._intro_shown:
            self._intro_shown = True
            path = os.path.join(DATA_DIR, "dialogue", self.cfg["intro"])
            self.game.push_scene(Dialogue.from_file(self.game, path))

    def on_exit(self):
        audio.music_stop()
        if self._alarm_chan:
            self._alarm_chan.stop()
            self._alarm_chan = None

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
        if self._alarm_chan:
            self._alarm_chan.stop()
            self._alarm_chan = None

    def _update_near(self):
        self._near = None
        for it in self.interactables:
            if not it.used and self.player.rect.colliderect(it.rect.inflate(26, 26)):
                self._near = it
                break

    def update(self, dt):
        self.player.update(dt, self.map)
        self.clock.update(dt)
        self._update_near()

        keys = pygame.key.get_pressed()
        term = self._near if (self._near and self._near.kind == "terminal"
                              and not self._near.used) else None
        investigating = bool(term and keys[pygame.K_e])

        NOISE_RADIUS = 220

        for en in self.entities:
            if investigating and pygame.Vector2(en.rect.center).distance_to(term.rect.center) < NOISE_RADIUS:
                en.lure_toward(term.rect.center, dt)
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
                    it.progress = max(0.0, it.progress - 0.05 * dt)

        seen = any(en.can_see(self.player, self.map) for en in self.entities)
        if seen and not self._seen_last:
            snd = audio.sound("alarm.wav")
            self._alarm_chan = snd.play(loops=-1) if snd else None   # ring while seen
        elif self._seen_last and not seen and self._alarm_chan:
            self._alarm_chan.stop()                                  # stop when safe
            self._alarm_chan = None
        self._seen_last = seen
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