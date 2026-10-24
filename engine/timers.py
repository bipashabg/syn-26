"""Small timing helpers."""


class Cooldown:
    """Returns True from ready() at most once per `interval` seconds."""
    def __init__(self, interval):
        self.interval = interval
        self.t = 0.0

    def update(self, dt):
        if self.t > 0:
            self.t -= dt

    def ready(self):
        if self.t <= 0:
            self.t = self.interval
            return True
        return False
