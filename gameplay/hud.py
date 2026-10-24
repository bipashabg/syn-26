"""Heads-up display — pixel / cyber styled.

Detection meter reads WHITE when you're safe and fills RED as you're seen, with
a bright border and pixel ticks so it's always visible. Plus the countdown and
the current objective. Drop assets/fonts/pixel.ttf to pixel-ify the text.
"""
import pygame

from engine import assets
from settings import WIDTH, HEIGHT

UI_FONT = "pixel.ttf"

DARK   = (11, 14, 26)
CYAN   = (95, 208, 255)
EMPTY  = (235, 240, 255)   # white = not detected
FILL   = (226, 60, 60)     # red   = detected
ACCENT = (122, 92, 255)
TEXT   = (230, 240, 255)


def _text(surf, font, s, x, y, color):
    surf.blit(font.render(s, True, DARK), (x + 1, y + 1))   # 1px shadow for contrast
    surf.blit(font.render(s, True, color), (x, y))


def draw_hud(surf, detection, objective, clock_label):
    f_small = assets.font(12, UI_FONT)
    f_med = assets.font(18, UI_FONT)

    # --- detection bar (top-left) ---
    bx, by, bw, bh = 20, 26, 240, 20
    pygame.draw.rect(surf, DARK, pygame.Rect(bx - 3, by - 3, bw + 6, bh + 6))       # backing
    pygame.draw.rect(surf, CYAN, pygame.Rect(bx - 3, by - 3, bw + 6, bh + 6), 2)    # frame
    pygame.draw.rect(surf, EMPTY, pygame.Rect(bx, by, bw, bh))                      # white empty
    fw = int(bw * max(0.0, min(1.0, detection)))
    if fw > 0:
        pygame.draw.rect(surf, FILL, pygame.Rect(bx, by, fw, bh))                   # red fill
    for i in range(1, 12):                                                          # pixel ticks
        x = bx + bw * i // 12
        pygame.draw.line(surf, DARK, (x, by), (x, by + bh - 1), 1)
    _text(surf, f_small, "DETECTION", bx, by + bh + 5, TEXT)
    if detection >= 1.0:
        msg = f_med.render("DETECTED", True, FILL)
        _text(surf, f_med, "DETECTED", WIDTH // 2 - msg.get_width() // 2, 26, FILL)

    # --- countdown (top-right) ---
    clk = f_med.render(clock_label, True, CYAN)
    _text(surf, f_med, clock_label, WIDTH - clk.get_width() - 24, 26, CYAN)

    # --- objective (bottom-left) ---
    _text(surf, f_small, objective, 20, HEIGHT - 26, TEXT)
