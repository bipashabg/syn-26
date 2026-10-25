import os
import pygame

from settings import ASSET_DIR

_sounds = {}
_ready = None


def _ensure():
    global _ready
    if _ready is not None:
        return _ready
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        _ready = True
    except Exception:
        _ready = False
    return _ready


def _path(name):
    return os.path.join(ASSET_DIR, "audio", name)


def sound(name):
    if not name or not _ensure():
        return None
    if name not in _sounds:
        try:
            p = _path(name)
            _sounds[name] = pygame.mixer.Sound(p) if os.path.exists(p) else None
        except Exception:
            _sounds[name] = None
    return _sounds[name]


def play(name, volume=1.0):
    s = sound(name)
    if s:
        try:
            s.set_volume(volume)
            s.play()
        except Exception:
            pass


def music_play(name, volume=0.5, loop=True):
    if not name or not _ensure():
        return
    p = _path(name)
    if not os.path.exists(p):
        return
    try:
        pygame.mixer.music.load(p)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1 if loop else 0)
    except Exception:
        pass


def music_stop(fade_ms=400):
    if not _ensure():
        return
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass