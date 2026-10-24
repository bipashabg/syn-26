"""Dilation clock — the shared countdown that gives the mindscape urgency.

Time spent in the mind burns real time in the facility (Interstellar-style
dilation). For the slice it's a simple countdown; in Stage 3 you can raise
`mind_cost` near the gravity-well center so diving deep costs more real time.
"""


class DilationClock:
    def __init__(self, ship_seconds=600):
        self.ship = float(ship_seconds)
        self.mind_cost = 1.0

    def update(self, dt):
        self.ship = max(0.0, self.ship - dt * self.mind_cost)

    @property
    def expired(self):
        return self.ship <= 0

    @property
    def label(self):
        m = int(self.ship // 60)
        s = int(self.ship % 60)
        return f"T-{m:02d}:{s:02d}"
