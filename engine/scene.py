
class Scene:
    transparent = False
    update_below = False

    def __init__(self, game):
        self.game = game

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, surface):
        pass


class SceneManager:
    def __init__(self):
        self.stack = []

    def push(self, scene):
        self.stack.append(scene)
        scene.on_enter()

    def pop(self):
        if self.stack:
            self.stack.pop().on_exit()

    def replace(self, scene):
        from engine import audio
        audio.play("transition.wav")
        self.pop()
        self.push(scene)

    @property
    def current(self):
        return self.stack[-1] if self.stack else None

    def handle_event(self, event):
        if self.current:
            self.current.handle_event(event)

    def update(self, dt):
        if not self.stack:
            return
        # update the top scene, plus any scene below it that opted in
        self.stack[-1].update(dt)
        for s in reversed(self.stack[:-1]):
            if s.update_below:
                s.update(dt)
            if not s.transparent:
                break

    def draw(self, surface):
        if not self.stack:
            return
        start = 0
        for i in range(len(self.stack) - 1, -1, -1):
            if not self.stack[i].transparent:
                start = i
                break
        for s in self.stack[start:]:
            s.draw(surface)
