"""Loading and story transition screens."""

import pygame

from engine.scene import Scene
from engine import assets
from settings import WIDTH, HEIGHT, COLORS


class LoadingScene(Scene):
    def __init__(
        self,
        game,
        duration=3.0,
        on_done=None,
        background_path=None,
        title="MINDTRACE",
        subtitle="ESTABLISHING NEURAL CONNECTION",
    ):
        super().__init__(game)

        self.duration = max(0.1, float(duration))
        self.elapsed = 0.0
        self.on_done = on_done
        self.finished = False

        self.title = title
        self.subtitle = subtitle
        self.background = None

        # Load the optional transition image.
        if background_path:
            try:
                image = pygame.image.load(background_path).convert()
                self.background = pygame.transform.smoothscale(
                    image, (WIDTH, HEIGHT)
                )
            except (pygame.error, OSError) as exc:
                print("Could not load transition image:", exc)

        # Dark overlay makes the loading text easier to read.
        self.overlay = pygame.Surface(
            (WIDTH, HEIGHT), pygame.SRCALPHA
        )
        self.overlay.fill((0, 0, 0, 115))

    def update(self, dt):
        if self.finished:
            return

        self.elapsed += dt

        if self.elapsed >= self.duration:
            self.finished = True

            if self.on_done:
                self.on_done()

    def draw(self, surf):
        # Show the story image, or use the regular dark background.
        if self.background:
            surf.blit(self.background, (0, 0))
            surf.blit(self.overlay, (0, 0))
        else:
            surf.fill((7, 11, 20))

        # Main title.
        if self.title:
            title_img = assets.font(34).render(
                self.title, True, COLORS["accent"]
            )
            surf.blit(
                title_img,
                (
                    WIDTH // 2 - title_img.get_width() // 2,
                    HEIGHT - 155,
                ),
            )

        # Story/loading subtitle.
        if self.subtitle:
            subtitle_img = assets.font(18).render(
                self.subtitle, True, COLORS["text"]
            )
            surf.blit(
                subtitle_img,
                (
                    WIDTH // 2 - subtitle_img.get_width() // 2,
                    HEIGHT - 105,
                ),
            )

        # Animated progress bar.
        progress = min(1.0, self.elapsed / self.duration)

        bar_width = 360
        bar_height = 8
        bar_x = (WIDTH - bar_width) // 2
        bar_y = HEIGHT - 65

        pygame.draw.rect(
            surf,
            (43, 49, 65),
            (bar_x, bar_y, bar_width, bar_height),
            border_radius=4,
        )

        pygame.draw.rect(
            surf,
            COLORS["accent"],
            (
                bar_x,
                bar_y,
                int(bar_width * progress),
                bar_height,
            ),
            border_radius=4,
        )

        dots = "." * (int(self.elapsed * 3) % 4)

        hint = assets.font(14).render(
            f"Loading next memory{dots}",
            True,
            COLORS["muted"],
        )

        surf.blit(
            hint,
            (
                WIDTH // 2 - hint.get_width() // 2,
                HEIGHT - 42,
            ),
        )