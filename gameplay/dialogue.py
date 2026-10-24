"""Dialogue / cutscene overlay. The single most important content system —
a story game lives or dies on it. Transparent, so the room shows behind it.

Lines are a list of dicts: {"speaker": str, "text": str, "portrait": str?}.
Your teammate writes these as JSON in data/dialogue/ — advance with Enter.
"""
import json
import os
import pygame

from engine.scene import Scene
from engine import assets
from settings import WIDTH, HEIGHT, COLORS


class Dialogue(Scene):
    transparent = True

    def __init__(self,
    game,
    lines,
    on_done=None,
    *,
    timed=False,
    music_path=None,
    music_start=0.0,
    music_volume=0.4,
    fallback_duration=42.0,):
        super().__init__(game)
        self.lines = lines
        self.idx = 0
        self.on_done = on_done
        
        # Music and timeline settings
        self.timed = timed
        self.music_path = music_path
        self.music_start = music_start
        self.music_volume = music_volume
        self.fallback_duration = fallback_duration

        # Timing state
        self.elapsed = 0.0
        self.timeline_time = 0.0
        self.music_active = False
        self.finished = False
        
        self._cinematic_backgrounds = {}
        
    @classmethod
    def from_file(
        cls,
        game,
        path,
        on_done=None,
        *,
        timed=False,
        music_path=None,
        music_start=0.0,
        music_volume=0.4,
        fallback_duration=42.0,
    ):
        with open(path, encoding="utf-8") as f:
            lines = json.load(f)

        return cls(
            game,
            lines,
            on_done,
            timed=timed,
            music_path=music_path,
            music_start=music_start,
            music_volume=music_volume,
            fallback_duration=fallback_duration,
        )
    
    def on_enter(self):
        # Normal gameplay dialogue should not start music.
        if not self.timed or not self.music_path:
            return

        try:
            pygame.mixer.music.load(self.music_path)
            pygame.mixer.music.set_volume(self.music_volume)

            pygame.mixer.music.play(
                loops=0,
                start=self.music_start,
                fade_ms=800,
            )

            self.music_active = True

        except (pygame.error, OSError, NotImplementedError) as exc:
            print("Could not play prologue music:", exc)
            self.music_active = False

    def on_exit(self):
        # Stop the prologue soundtrack when leaving the cinematic.
        if self.music_active:
            pygame.mixer.music.stop()
            self.music_active = False

    def _finish(self):
        # Prevent completing the same scene twice.
        if self.finished:
            return

        self.finished = True
        self.game.pop_scene()

        if self.on_done:
            self.on_done()

    def update(self, dt):
        if not self.timed or self.finished:
            return

        self.elapsed += dt

        if self.music_active and pygame.mixer.music.get_busy():
            pos_ms = pygame.mixer.music.get_pos()

            if pos_ms >= 0:
                self.timeline_time = pos_ms / 1000.0
            else:
                self.timeline_time = self.elapsed
        else:
            self.timeline_time = self.elapsed

        # Select the most recent dialogue cue whose time has arrived.
        for i, line in enumerate(self.lines):
            cue_time = float(line.get("at", 0.0))

            if cue_time <= self.timeline_time:
                self.idx = i
            else:
                break

        # Finish when the configured cinematic duration is reached.
        if self.timeline_time >= self.fallback_duration:
            self._finish()
            return

        # Also finish if the soundtrack ends naturally.
        if (
            self.music_active
            and self.elapsed > 0.5
            and not pygame.mixer.music.get_busy()
        ):
            self._finish()
        
    def handle_event(self, e):
        if e.type != pygame.KEYDOWN:
            return

        # Timed cinematics advance automatically.
        if self.timed:
            if e.key == pygame.K_ESCAPE:
                self._finish()
            return

        # Normal gameplay dialogues remain manually controlled.
        if e.key in (
            pygame.K_RETURN,
            pygame.K_SPACE,
            pygame.K_e,
        ):
            self.idx += 1

            if self.idx >= len(self.lines):
                self._finish()

    def draw(self, surf):
        if self.idx >= len(self.lines):
            return

        line = self.lines[self.idx]

        # Does this dialogue entry have a cinematic image?
        image_path = line.get("image")

        if image_path:
            # Draw the full-screen background first.
            self._draw_cinematic_background(surf, image_path)

            # Position the caption panel near the bottom.
            box = pygame.Rect(
                24,
                HEIGHT - 132,
                WIDTH - 48,
                108
            )

            # Create a translucent black background.
            panel = pygame.Surface(box.size, pygame.SRCALPHA)
            panel.fill((10, 12, 18, 224))
            surf.blit(panel, box.topleft)

        else:
            # Keep the original appearance for normal dialogue.
            box = pygame.Rect(
                40,
                HEIGHT - 170,
                WIDTH - 80,
                130
            )

            pygame.draw.rect(
                surf, COLORS["box"], box,
                border_radius=10
            )

        # Draw the panel border.
        pygame.draw.rect(
            surf, COLORS["box_border"], box,
            2, border_radius=10
        )

        # Draw the speaker's name.
        speaker = assets.font(20).render(
            line.get("speaker", ""),
            True,
            COLORS["accent"]
        )

        surf.blit(speaker, (box.x + 18, box.y + 12))

        # Draw the dialogue text, with automatic line wrapping.
        self._wrapped(
            surf,
            line.get("text", ""),
            box.x + 18,
            box.y + 43,
            box.width - 36,
            assets.font(19)
        )

        hint_text = (
            "ESC: SKIP CINEMATIC"
            if self.timed
            else "Enter / Space ▸"
        )

        hint = assets.font(14).render(
            hint_text,
            True,
            COLORS["muted"]
        )

        surf.blit(
            hint,
            (box.right - hint.get_width() - 14, box.bottom - 22)
        )

    def _wrapped(self, surf, text, x, y, w, font):
        line, yy = "", y
        for word in text.split():
            test = (line + " " + word).strip()
            if font.size(test)[0] > w and line:
                surf.blit(font.render(line, True, COLORS["text"]), (x, yy))
                yy += 26
                line = word
            else:
                line = test
        if line:
            surf.blit(font.render(line, True, COLORS["text"]), (x, yy))

    def _draw_cinematic_background(self, surf, image_path):
        if image_path not in self._cinematic_backgrounds:
            source = assets.image(image_path)

            source_w, source_h = source.get_size()

            # Scale the image enough to cover the entire window.
            scale = max(
                WIDTH / source_w,
                HEIGHT / source_h
            )

            target_size = (
                round(source_w * scale),
                round(source_h * scale)
            )

            background = pygame.transform.smoothscale(
                source, target_size
            )

            self._cinematic_backgrounds[image_path] = background

        background = self._cinematic_backgrounds[image_path]

        # Center the image. Any excess edges are cropped by the window.
        destination = background.get_rect(
            center=(WIDTH // 2, HEIGHT // 2)
        )

        surf.blit(background, destination)