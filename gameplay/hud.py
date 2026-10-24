"""Heads-up display: detection meter, countdown, and current objective."""
import pygame

from engine import assets
from settings import WIDTH, HEIGHT, COLORS


def draw_hud(surf, detection, objective, clock_label):
    # detection meter (top-left)
    track = pygame.Rect(20, 20, 200, 16)
    pygame.draw.rect(surf, (40, 40, 52), track, border_radius=8)
    fill_w = int(200 * max(0.0, min(1.0, detection)))
    color = COLORS["alert"] if detection > 0.6 else COLORS["accent"]
    if fill_w > 0:
        pygame.draw.rect(surf, color, pygame.Rect(20, 20, fill_w, 16), border_radius=8)
    surf.blit(assets.font(13).render("detection", True, COLORS["muted"]), (20, 40))
    if detection >= 1.0:
        warn = assets.font(18).render("DETECTED", True, COLORS["alert"])
        surf.blit(warn, (WIDTH // 2 - warn.get_width() // 2, 24))

    # countdown (top-right)
    clk = assets.font(22).render(clock_label, True, COLORS["accent"])
    surf.blit(clk, (WIDTH - clk.get_width() - 24, 20))

    # objective (bottom-left)
    obj = assets.font(16).render(objective, True, COLORS["text"])
    surf.blit(obj, (20, HEIGHT - 30))
