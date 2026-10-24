import pygame

from engine.scene import Scene
from engine import assets
from settings import WIDTH, HEIGHT, COLORS


class LoadingScene(Scene):

    def __init__(self, game, duration=3.0, on_done=None):
        super().__init__(game)

        self.duration = duration
        self.elapsed = 0.0
        self.on_done = on_done
        self.finished = False

    def update(self, dt):
        if self.finished:
            return

        self.elapsed += dt

        if self.elapsed >= self.duration:
            self.finished = True

            if self.on_done:
                self.on_done()

    def draw(self, surf):
        # 1. Draw a dark background.
        surf.fill((7, 11, 20))

        # 2. Draw the game title.
        title = assets.font(42).render(
            "MINDTRACE",
            True,
            COLORS["accent"]
        )

        surf.blit(
            title,
            (
                WIDTH // 2 - title.get_width() // 2,
                HEIGHT // 2 - 100
            )
        )

        # 3. Draw a loading message.
        message = assets.font(20).render(
            "ESTABLISHING NEURAL CONNECTION",
            True,
            COLORS["text"]
        )

        surf.blit(
            message,
            (
                WIDTH // 2 - message.get_width() // 2,
                HEIGHT // 2 - 30
            )
        )

        # 4. Calculate the progress of the delay.
        progress = min(
            1.0,
            self.elapsed / self.duration
        )

        # 5. Draw the loading bar's background.
        bar_width = 360
        bar_height = 10

        bar_x = (WIDTH - bar_width) // 2
        bar_y = HEIGHT // 2 + 20

        pygame.draw.rect(
            surf,
            (43, 49, 65),
            (bar_x, bar_y, bar_width, bar_height),
            border_radius=5
        )

        # 6. Draw the filled portion of the bar.
        pygame.draw.rect(
            surf,
            COLORS["accent"],
            (
                bar_x,
                bar_y,
                int(bar_width * progress),
                bar_height
            ),
            border_radius=5
        )

        # 7. Animate the dots after the text.
        dots = "." * (int(self.elapsed * 3) % 4)

        hint = assets.font(16).render(
            f"Reconstructing memory{dots}",
            True,
            COLORS["muted"]
        )

        surf.blit(
            hint,
            (
                WIDTH // 2 - hint.get_width() // 2,
                bar_y + 24
            )
        )