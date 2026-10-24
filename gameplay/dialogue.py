"""Dialogue / cutscene overlay. The single most important content system —
a story game lives or dies on it. Transparent, so the room shows behind it.

Lines are a list of dicts: {"speaker": str, "text": str, "portrait": str?}.
Your teammate writes these as JSON in data/dialogue/ — advance with Enter.
"""
import json
import pygame

from engine.scene import Scene
from engine import assets
from settings import WIDTH, HEIGHT, COLORS


class Dialogue(Scene):
    transparent = True

    def __init__(self, game, lines, on_done=None):
        super().__init__(game)
        self.lines = lines
        self.idx = 0
        self.on_done = on_done
        self._cinematic_backgrounds = {}

    @classmethod
    def from_file(cls, game, path, on_done=None):
        with open(path) as f:
            return cls(game, json.load(f), on_done)

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN and e.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
            self.idx += 1
            if self.idx >= len(self.lines):
                self.game.pop_scene()
                if self.on_done:
                    self.on_done()

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

        # Draw the input hint.
        hint = assets.font(14).render(
            "Enter / Space ▸",
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