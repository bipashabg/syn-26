"""UNTITLED — entry point. Run with:  python main.py"""
from engine.game import Game
from scenes.title import TitleScene


def main():
    game = Game()
    game.push_scene(TitleScene(game))
    game.run()


if __name__ == "__main__":
    main()
