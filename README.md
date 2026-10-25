# NAME

A 2D top-down stealth and narrative-mystery game built in Python with pygame.
The player descends into the fractured memories of a comatose scientist to
recover a lost emergency shutdown procedure before a catastrophe reactivates.

Built for a hackathon. Genre influences: Metal Gear Solid (stealth and vision
cones), Pokemon-style top-down exploration, and the tone of Interstellar and
Inception (black holes, time dilation, descending through layers of the mind).
<img width="966" height="635" alt="Screenshot 2026-10-25 054405" src="https://github.com/user-attachments/assets/9883c0de-5510-4119-b7a3-2a5114e7b5e4" />

<img width="967" height="631" alt="Screenshot 2026-10-25 054420" src="https://github.com/user-attachments/assets/b54f1614-0649-40d9-9b9c-4baa3ec232d0" />


---

## Premise

Dr. Arin Rao was studying a mysterious signal near a black hole aboard the
research vessel when an experiment went catastrophically wrong. He was found
unconscious and remained in a coma for seven years. Now the unstable remnant of
that experiment is about to reactivate, threatening disaster. The only person
who knows the shutdown procedure is Arin, but his memories are fragmented.

A recovery team initiates a neural connection and the player enters Arin's mind.
An unfamiliar voice guides the descent through three increasingly unstable layers
of memory. The player evades corrupted memories, investigates what really
happened, and reconstructs the shutdown sequence. The identity of the guiding
voice, and the truth of what Arin did, are revealed at the climax.

The game ends on a final choice with two distinct outcomes.

---

## Requirements and running

- Python 3.10 or newer
- pygame-ce (the maintained community fork of pygame)
- Pillow (optional, only used for the animated GIF backdrop; the game falls
  back to a procedural starfield if it is absent)

```bash
pip install -r requirements.txt   # pygame-ce, pillow
python main.py
```

Audio note: on WSL, audio must be routed to the host (PulseAudio via WSLg).
The game runs with full audio natively on Windows, macOS, and most Linux desktops.

---

## Controls

| Input                | Action                                             |
| -------------------- | -------------------------------------------------- |
| WASD or Arrow keys   | Move                                               |
| Shift (hold)         | Crouch (slower, hides you in cover tiles)          |
| E                    | Interact; hold E to investigate a terminal/console |
| Enter / Space / E    | Advance dialogue                                   |
| Mouse / number keys  | Order fragments in the reconstruction puzzle       |
| T / R (ending)       | Transmit the truth / Reset the loop                |
| Esc                  | Skip a cinematic, or quit                          |

---

## Gameplay overview

The game is a sequence of scenes:

```
Title  ->  Prologue (cinematic)  ->  Stage 1  ->  Stage 2  ->  Stage 3  ->  Ending
```

Each playable stage shares one core loop: explore a top-down room, avoid a
patrolling corrupted memory using line-of-sight stealth, reach an interactable
console and investigate it (which takes time and makes noise), recover a clue,
and move on. Later stages layer on an environmental hazard and a memory-ordering
puzzle.

- Stage 1 - The Forgotten Station: stealth and terminal investigation.
- Stage 2 - The Tidal Archive: adds the Memory Tide hazard.
- Stage 3 - The Core Memory: combines patrols, the hazard, the final recording,
  and the shutdown-sequence reconstruction, then the ending.

---

## Core mechanics

- Stealth and detection. Each enemy patrols a path and projects a vision cone
  (range and angle) with a line-of-sight check against walls. If the player is
  inside the cone, in line of sight, and not crouched in cover, a detection
  meter fills; when full, the player is returned to the stage checkpoint. An
  alarm sound loops while the player is seen and stops when they are safe.

- Terminal investigation and noise. Consoles are held (not tapped) to
  investigate over a few seconds, filling a progress bar. Investigating emits
  noise: enemies within a noise radius are lured toward the console. Progress
  persists if the player backs off, so a terminal can be finished across several
  safe windows.

- Memory Tide hazard. A periodic wave sweeps the room on a cycle (idle,
  warning, active). While a wave is active, a player who is not standing in a
  safe zone (a cover tile) is caught. The warning phase gives time to reach
  cover. It is a timed hazard, not a physics simulation.

- Memory reconstruction. An interactive puzzle where scattered memory fragments
  must be placed into a timeline in the correct order. The correct order reveals
  the true memory; a wrong order plays a false memory and lets the player retry.

- Dilation clock. A countdown that frames the urgency of the dive, themed on the
  time dilation near the black hole.

---

## Architecture

### Design principles

1. Scene stack. The entire game is a stack of scenes managed by a central
   SceneManager. Rooms, the title, the loading screen, and the ending are
   scenes; dialogue, cutscenes, and the reconstruction puzzle are transparent
   overlay scenes pushed on top that pause what is below. This makes it trivial
   to interrupt gameplay with a conversation and return to it.

2. Data-driven content. Levels, conversations, and puzzle definitions live in
   plain data files, not code. Room layouts are CSV grids, dialogue and puzzle
   content are JSON. A stage is defined by a small configuration dictionary. This
   separation let two developers work in parallel: one on engine and systems,
   one on content, rooms, and narrative, with minimal file overlap.

3. Graceful degradation. Missing assets never crash the game. A missing sprite
   falls back to a drawn colored shape, a missing font to a system font, a
   missing sound to silence, and a missing GIF to a procedural starfield. This
   let the game run and be tested long before the art and audio existed.

### Layered structure

```
engine/     Reusable core. Knows nothing about this specific game.
gameplay/   Game-specific systems built on the engine.
scenes/     One file per stage or screen; wires systems and content together.
data/       Content as data: rooms (CSV), dialogue and puzzles (JSON).
assets/     Images, audio, fonts.
```

Dependency direction is one-way: scenes depend on gameplay, gameplay depends on
engine, engine depends only on settings. The engine never imports upward.

### Directory layout

```
mindtrace/
├── main.py                 Entry point: builds the Game and pushes the title scene
├── settings.py             Constants and theme (screen size, tile size, colors, tuning)
├── requirements.txt
│
├── engine/                 Reusable core
│   ├── game.py             Game: window, clock, main loop, owns the SceneManager
│   ├── scene.py            Scene base class + stack-based SceneManager
│   ├── camera.py           Follow camera, world-to-screen transform, clamped to map
│   ├── tilemap.py          Loads a CSV room; draws tiles; wall/cover collision geometry
│   ├── entity.py           Base entity (position, rect)
│   ├── assets.py           Cached loading of images, fonts, sprites, with safe fallbacks
│   ├── audio.py            Lazy-init mixer; music and sound-effect playback helpers
│   ├── anim.py             SpaceBackdrop: animated GIF backdrop or procedural starfield
│   └── timers.py           Small timing helpers
│
├── gameplay/               Game-specific systems
│   ├── player.py           Player movement, crouch, axis-separated wall collision
│   ├── enemy.py            StealthEntity: patrol, vision cone, line of sight, lure
│   ├── interactable.py     Logs, fragments, exits, and hold-to-investigate terminals
│   ├── dialogue.py         Dialogue overlay: typewriter mode and timed cinematic mode
│   ├── reconstruction.py   The interactive memory-weave ordering puzzle
│   ├── hazard.py           MemoryTide: the periodic environmental hazard
│   ├── hud.py              Detection meter, countdown, objective text
│   └── dilation.py         DilationClock: the countdown resource
│
├── scenes/                 Stages and screens
│   ├── title.py            Title screen and menu music
│   ├── prologue.py         Opening cinematic, then the first loading transition
│   ├── loading.py          Loading / story transition screen with progress bar
│   ├── stage_base.py       StageScene: the reusable playable stage, driven by config
│   ├── stage1_static.py    Stage 1 configuration and content
│   ├── stage2_corruption.py Stage 2 configuration and content
│   ├── stage3_horizon.py   Stage 3 configuration, Memory Tide wiring, finale routing
│   └── ending.py           Final choice, cinematic truth ending, and reset outcome
│
├── data/
│   ├── rooms/              CSV grids: 0 floor, 1 wall, 2 cover
│   ├── dialogue/           JSON conversations and clue text
│   └── anomalies.json      Reconstruction puzzle fragment sets
│
└── assets/
    ├── images/             Sprites, tiles, per-stage skins, transition art
    ├── audio/              Music tracks and sound effects
    └── fonts/              Pixel font (optional; falls back to a system mono font)
```

### Game loop and scene flow

`main.py` creates `Game`, which opens the window, holds the clock and the
`SceneManager`, and runs the loop. Each frame it computes delta time, dispatches
input to the top scene, updates, and draws.

The `SceneManager` holds a stack. `push` adds a scene and calls its `on_enter`;
`pop` removes one and calls its `on_exit`; `replace` does both. Drawing walks
down from the top to the first non-transparent scene and renders upward, so
overlays composite over the gameplay beneath them. Updates go to the top scene
only, which is why pushing a dialogue overlay naturally pauses the stage.

Scene transitions:

```
TitleScene ──Enter──▶ PrologueScene ──cinematic done──▶ LoadingScene
                                                              │
                                                              ▼
Stage 1 ──terminal clue / exit──▶ LoadingScene ──▶ Stage 2 ──▶ ... ──▶ Stage 3
                                                                           │
                                                 reconstruct shutdown ─────┤
                                                                           ▼
                                                                     EndingScene
                                                         (choice: Transmit / Reset)
```

### Stage configuration

Every playable stage is an instance of `StageScene`, configured by a dictionary
rather than subclassed, so adding a stage is mostly data:

```python
cfg = {
    "room": "stage1.csv",                 # CSV room in data/rooms/
    "spawn": (96, 96),                    # player start, in pixels
    "objective": "Reach the terminal.",   # HUD text
    "time": 600,                          # dilation-clock seconds
    "entity_speed": 55,
    "patrols": [[(200, 140), (1000, 140), (1000, 640), (240, 600)]],
    "interactables": [ ... ],             # Interactable objects
    "intro": "stage1.json",               # dialogue played on entry
    "music": "stage1_music.wav",          # background track
    "tiles": {0: "floor.png", 1: "wall.png", 2: "cover.png"},  # per-stage skin
    "enemy_sprite": "enemy.png",
    "next": go_next,                       # callable(game) to advance
}
```

Stage 3 subclasses `StageScene` to add the Memory Tide and route the finale
through the final recording, the reconstruction puzzle, and the ending.

### Key systems

- Rendering and tiles. `TileMap` loads a CSV grid where 0 is floor, 1 is wall,
  and 2 is cover. It builds collision rectangles for walls and cover and draws
  each tile from a per-stage sprite set, falling back to flat colors. The
  `Camera` follows the player and clamps to the map bounds.

- Stealth. `StealthEntity` walks a loop of waypoints, faces its direction of
  travel, and exposes `can_see(player)` which tests range, cone angle, cover,
  and a stepped line-of-sight ray against walls. `lure_toward(point)` overrides
  the patrol when the console noise attracts it.

- Dialogue, two modes. `Dialogue` is a transparent overlay. In normal mode it
  types text out character by character; the type sound loops only while text is
  revealing and stops when the line is complete or the box closes. In timed
  cinematic mode it plays a music track, advances lines on a timeline using each
  line's "at" timestamp, renders full-screen background images per line, and
  auto-finishes when the track ends. The prologue and the truth ending use the
  cinematic mode.

- Audio. `engine/audio.py` lazily initializes the mixer and exposes
  `music_play`, `music_stop`, `sound`, and `play`. Music streams one track at a
  time and stops cleanly on scene change. Sound effects follow one rule
  throughout: loop while their moment is active, stop the instant it ends,
  regardless of clip length. This governs the typing tick, the detection alarm,
  and the loading transition.

- Per-stage asset skinning. Tiles and the enemy sprite are chosen per stage via
  the stage config, so each stage can have its own look while the player and
  terminal sprites stay shared. `TileMap` and `StageScene` read both `tiles` and
  `tile_sprites` keys for compatibility.

---

## Authoring content

- Add or edit a room: create a CSV grid in `data/rooms/` using 0 (floor),
  1 (wall), 2 (cover). Pixels equal tile index times the tile size in
  `settings.py`.

- Add or edit dialogue: edit the JSON files in `data/dialogue/`. A line is
  `{"speaker": "...", "text": "..."}`. Cinematic lines also take `"at"` (seconds)
  and `"image"` (a full-screen background filename).

- Add a stage: write a `make(game)` function that builds a config dictionary and
  calls `game.replace_scene(StageScene(game, cfg))`, and chain it from the
  previous stage's `next`.

- Tuning: speeds, vision range and angle, detection rates, tile size, and colors
  live in `settings.py`.

---

## Technology

- Language: Python 3
- Framework: pygame-ce
- Optional: Pillow
- No other runtime dependencies; all game logic is self-contained.

