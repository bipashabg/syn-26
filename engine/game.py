"""Game: owns the window, clock and scene stack, and runs the main loop."""
import pygame

from engine.scene import SceneManager
from settings import WIDTH, HEIGHT, FPS, COLORS


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("UNTITLED")
        self.clock = pygame.time.Clock()
        self.manager = SceneManager()
        self.running = True

    # convenience wrappers so scenes can drive transitions
    def push_scene(self, scene):
        self.manager.push(scene)

    def replace_scene(self, scene):
        self.manager.replace(scene)

    def pop_scene(self):
        self.manager.pop()

    def quit(self):
        self.running = False

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)  # clamp after a stall so physics don't jump
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.manager.handle_event(event)

            self.manager.update(dt)
            if not self.manager.stack:
                self.running = False
                break

            self.screen.fill(COLORS["bg"])
            self.manager.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
