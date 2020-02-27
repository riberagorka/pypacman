import time
import tkinter as tk
from typing import Type

from agent import Agent
from graphics import PacmanGraphics
from game import Direction, Game

__all__ = ['Application']


class Application(tk.Frame):
    UNIT_SIZE = 40
    PACMAN_WAKAS_PER_SECOND = 2.0

    INPUT = {
        'w': Direction.North,
        'a': Direction.West,
        's': Direction.South,
        'd': Direction.East,

        'Up': Direction.North,
        'Left': Direction.West,
        'Down': Direction.South,
        'Right': Direction.East,
    }

    def __init__(self, layout: [str], pacman: Type[Agent], ghost: Type[Agent], n_ghosts: int, frame_rate: int):
        self.game = Game(layout, pacman, ghost, n_ghosts)

        self.window = tk.Tk()
        self.window.geometry(
            f'{Application.UNIT_SIZE * (2 + self.game.map.width)}x'
            f'{Application.UNIT_SIZE * (3 + self.game.map.height)}+450+250')

        super().__init__(self.window)
        self.pack(fill=tk.BOTH, expand=True)

        for key in ['w', 'a', 's', 'd', 'Up', 'Left', 'Down', 'Right']:
            self.window.bind(f'<{key}>', self._handle_key_press)

        self.graphics = PacmanGraphics(
            self,
            0.0 if frame_rate == 0 else 1.0 / float(frame_rate),
            Application.UNIT_SIZE,
            (self.game.map.width, self.game.map.height)
        )
        self.graphics.draw_map(self.game.map.walls)

    def reset(self):
        self.game.reset()

    def run(self):
        previous_time = time.time()
        while self.game.is_running():
            try:
                current_time = time.time()
                if current_time - previous_time >= self.graphics.frame_rate:
                    previous_time = current_time
                    self.game.update()
                self.graphics.draw(self.game, current_time - previous_time)
                self.update()

            except KeyboardInterrupt:
                break

        self.quit()

    # MARK: Private

    def _handle_key_press(self, event):
        if event.keysym in Application.INPUT:
            self.game.pacman.keyboard_direction = Application.INPUT[event.keysym]
