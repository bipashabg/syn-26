
import json
import pygame

from engine.scene import Scene
from engine import assets, audio
from settings import WIDTH, HEIGHT

UI_FONT = "pixel.ttf"
CHARS_PER_SEC = 45          # typewriter speed
TYPE_SOUND = "type.wav"

PANEL  = (13, 16, 34)
FRAME  = (95, 208, 255)
INNER  = (43, 108, 230)
ACCENT = (122, 92, 255)
TEXT   = (230, 240, 255)
MUTED  = (120, 140, 190)


class Dialogue(Scene):
    transparent = True

    def __init__(self, game, lines, on_done=None, *,
                 timed=False, music_path=None, music_start=0.0,
                 music_volume=0.4, fallback_duration=42.0):
        super().__init__(game)
        self.lines = lines
        self.idx = 0
        self.on_done = on_done

        # cinematic / timed-mode settings
        self.timed = timed
        self.music_path = music_path
        self.music_start = music_start
        self.music_volume = music_volume
        self.fallback_duration = fallback_duration

        # typewriter state (normal mode)
        self.shown = 0.0
        self._type_chan = None     # looping type-sound channel while typing

        # timing / lifecycle state
        self.elapsed = 0.0
        self.timeline_time = 0.0
        self.music_active = False
        self.finished = False
        self._cinematic_backgrounds = {}

    @classmethod
    def from_file(cls, game, path, on_done=None, *,
                  timed=False, music_path=None, music_start=0.0,
                  music_volume=0.4, fallback_duration=42.0):
        with open(path, encoding="utf-8-sig") as f:   # utf-8-sig swallows Windows BOMs
            lines = json.load(f)
        return cls(game, lines, on_done, timed=timed, music_path=music_path,
                   music_start=music_start, music_volume=music_volume,
                   fallback_duration=fallback_duration)

    # ---------- lifecycle ----------
    def on_enter(self):
        if not self.timed or not self.music_path:
            return
        try:
            pygame.mixer.music.load(self.music_path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops=0, start=self.music_start, fade_ms=800)
            self.music_active = True
        except (pygame.error, OSError, NotImplementedError) as exc:
            print("Could not play cinematic music:", exc)
            self.music_active = False

    def on_exit(self):
        self._stop_type()
        if self.music_active:
            try:
                pygame.mixer.music.stop()
            except pygame.error:
                pass
            self.music_active = False

    def _stop_type(self):
        if self._type_chan:
            try:
                self._type_chan.stop()
            except Exception:
                pass
        self._type_chan = None

    def _finish(self):
        if self.finished:
            return
        self.finished = True
        self.game.pop_scene()
        if self.on_done:
            self.on_done()

    def _text(self):
        if self.idx < len(self.lines):
            return self.lines[self.idx].get("text", "")
        return ""

    # ---------- update ----------
    def update(self, dt):
        if self.timed:
            self._update_timed(dt)
        else:
            self._update_typewriter(dt)

    def _update_typewriter(self, dt):
        text = self._text()
        if self.shown < len(text):
            if self._type_chan is None:                 # start the loop while typing
                snd = audio.sound(TYPE_SOUND)
                self._type_chan = snd.play(loops=-1) if snd else False
            self.shown = min(len(text), self.shown + CHARS_PER_SEC * dt)
            if self.shown >= len(text):                 # line fully shown -> silence
                self._stop_type()

    def _update_timed(self, dt):
        if self.finished:
            return
        self.elapsed += dt
        if self.music_active and pygame.mixer.music.get_busy():
            pos_ms = pygame.mixer.music.get_pos()
            self.timeline_time = pos_ms / 1000.0 if pos_ms >= 0 else self.elapsed
        else:
            self.timeline_time = self.elapsed

        for i, line in enumerate(self.lines):
            if float(line.get("at", 0.0)) <= self.timeline_time:
                self.idx = i
            else:
                break

        if self.timeline_time >= self.fallback_duration:
            self._finish()
            return
        if self.music_active and self.elapsed > 0.5 and not pygame.mixer.music.get_busy():
            self._finish()

    # ---------- input ----------
    def handle_event(self, e):
        if e.type != pygame.KEYDOWN:
            return
        if self.timed:
            if e.key == pygame.K_ESCAPE:
                self._finish()
            return
        if e.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
            text = self._text()
            if self.shown < len(text):
                self.shown = len(text)          # reveal the rest
                self._stop_type()
            else:
                self.idx += 1                   # advance
                self.shown = 0.0
                self._stop_type()
                if self.idx >= len(self.lines):
                    self._finish()

    # ---------- draw ----------
    def draw(self, surf):
        if self.idx >= len(self.lines):
            return
        line = self.lines[self.idx]
        full = line.get("text", "")
        shown_text = full if self.timed else full[:int(self.shown)]
        image_path = line.get("image")

        if image_path:
            self._draw_cinematic_background(surf, image_path)
            
            if line.get("flash", False): return
            
            box = pygame.Rect(24, HEIGHT - 132, WIDTH - 48, 108)
            panel = pygame.Surface(box.size, pygame.SRCALPHA)
            panel.fill((10, 12, 18, 224))
            surf.blit(panel, box.topleft)
            pygame.draw.rect(surf, FRAME, box, 2)
        else:
            box = pygame.Rect(30, HEIGHT - 150, WIDTH - 60, 120)
            pygame.draw.rect(surf, PANEL, box)
            pygame.draw.rect(surf, FRAME, box, 3)
            pygame.draw.rect(surf, INNER, box.inflate(-10, -10), 1)
            for cx, cy in ((box.left, box.top), (box.right - 6, box.top),
                           (box.left, box.bottom - 6), (box.right - 6, box.bottom - 6)):
                pygame.draw.rect(surf, ACCENT, pygame.Rect(cx, cy, 6, 6))

        surf.blit(assets.font(18, UI_FONT).render(line.get("speaker", ""), True, ACCENT),
                  (box.x + 18, box.y + 14))
        self._wrapped(surf, shown_text, box.x + 18, box.y + 46,
                      box.width - 36, assets.font(15, UI_FONT))

        if self.timed:
            hint = assets.font(12, UI_FONT).render("Esc ▸ skip", True, MUTED)
            surf.blit(hint, (box.right - hint.get_width() - 16, box.bottom - 24))
        elif self.shown >= len(full):
            hint = assets.font(12, UI_FONT).render("Enter ▸", True, MUTED)
            surf.blit(hint, (box.right - hint.get_width() - 16, box.bottom - 24))

    def _wrapped(self, surf, text, x, y, w, font):
        line, yy = "", y
        for word in text.split():
            test = (line + " " + word).strip()
            if font.size(test)[0] > w and line:
                surf.blit(font.render(line, True, TEXT), (x, yy))
                yy += font.get_height() + 6
                line = word
            else:
                line = test
        if line:
            surf.blit(font.render(line, True, TEXT), (x, yy))

    def _draw_cinematic_background(self, surf, image_path):
        if image_path not in self._cinematic_backgrounds:
            source = assets.image(image_path)
            sw, sh = source.get_size()
            scale = max(WIDTH / sw, HEIGHT / sh)
            scaled = pygame.transform.smoothscale(
                source, (round(sw * scale), round(sh * scale)))
            self._cinematic_backgrounds[image_path] = scaled
        bg = self._cinematic_backgrounds[image_path]
        surf.blit(bg, bg.get_rect(center=(WIDTH // 2, HEIGHT // 2)))