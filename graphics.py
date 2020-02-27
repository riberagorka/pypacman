import math
import time
import tkinter as tk
from agent import Agent
from game import Game

__all__ = ['Graphics', 'PacmanGraphics']


QUAD_MODEL = [
    (-0.5, -0.5),
    (0.5, -0.5),
    (0.5, 0.5),
    (-0.5, 0.5)
]

GHOST_MODEL = [
    (0, 0.5),
    (0.25, 0.75),
    (0.5, 0.5),
    (0.75, 0.75),
    (0.75, -0.5),
    (0.5, -0.75),
    (-0.5, -0.75),
    (-0.75, -0.5),
    (-0.75, 0.75),
    (-0.5, 0.5),
    (-0.25, 0.75)
]


class Graphics:
    def __init__(self, app: tk.Frame):
        self._canvas = tk.Canvas(app)
        self._canvas.configure(background='black')
        self._canvas.pack(fill=tk.BOTH, expand=True)
        self.objects = []

    def clear(self):
        self._canvas.delete(*self.objects)
        self.objects.clear()

    def draw_arc(self,
                 x: float,
                 y: float,
                 radius: float,
                 angle=359.99,
                 start_angle=0.0,
                 color="#fb0",
                 border="#000",
                 permanent=False):

        self._add_object(
            self._canvas.create_arc(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                start=start_angle,
                extent=angle,
                fill=color,
                outline=border
            ),
            permanent
        )

    def draw_polygon(self,
                     points: [(float, float)],
                     width=1.0,
                     smooth=False,
                     color="#fb0",
                     border="#000",
                     permanent=False):

        coordinates = []
        for point in points:
            coordinates.extend(point)

        self._add_object(
            self._canvas.create_polygon(
                coordinates,
                width=width,
                smooth=smooth,
                fill=color,
                outline=border
            ),
            permanent
        )

    def draw_rect(self,
                  x: float,
                  y: float,
                  width: float,
                  height: float,
                  color="#fb0",
                  border="#000",
                  permanent=False):

        self._add_object(
            self._canvas.create_rectangle(
                x,
                y,
                x + width,
                y + height,
                fill=color,
                outline=border
            ),
            permanent
        )

    def draw_models(self,
                    size: float,
                    model: [(float, float)],
                    positions: [(float, float)],
                    width=1.0,
                    smooth=True,
                    colors: [str] = None,
                    borders: [str] = None,
                    permanent=False):

        colors = colors or ["#fb0" for _ in range(len(positions))]
        borders = borders or ["#000" for _ in range(len(positions))]
        vertices = list(range(len(model)))
        for position, color, border in zip(positions, colors, borders):
            for i, vertex in enumerate(model):
                vertices[i] = position[0] + vertex[0] * size, position[1] + vertex[1] * size
            self.draw_polygon(vertices, width=width, smooth=smooth, color=color, border=border, permanent=permanent)

    def draw_text(self,
                  x: float,
                  y: float,
                  text: str,
                  font="Helvetica 12 normal",
                  anchor="nw",
                  color="#fff",
                  permanent=False):

        self._add_object(
            self._canvas.create_text(
                x,
                y,
                text=text,
                font=font.split(' '),
                anchor=anchor,
                fill=color,
            ),
            permanent
        )

    # MARK: Private

    def _add_object(self, object_id, permanent):
        if not permanent:
            self.objects.append(object_id)


class PacmanGraphics:

    PACMAN_WAKAS_PER_SECOND = 2.0

    def __init__(self, app: tk.Frame, frame_rate: float, unit_size: float, map_size: (int, int)):
        self.game = app.game  # this is ugly, remove this
        self.graphics = Graphics(app)
        self.frame_rate = frame_rate or 1e-8
        self.unit_size = unit_size
        self.width, self.height = map_size

    def draw_map(self, walls: [[bool]]):
        self._draw_map(walls)

    def draw(self, game: Game, dt: float):
        self.graphics.clear()
        self._draw_info(game.score, game.pacman, game.ghosts)
        self._draw_food(game.map.food)
        self._draw_ghosts(game.ghosts, dt)
        self._draw_pacman(game.pacman, dt)

    # MARK: Private

    def _animate_position(self, agent: Agent, dt: float) -> (float, float):
        position = self._get_screen_position(*agent.position)
        previous_position = self._get_screen_position(*agent.previous_position)
        ratio = min(1.0, dt / self.frame_rate)
        return \
            position[0] * ratio + previous_position[0] * (1.0 - ratio), \
            position[1] * ratio + previous_position[1] * (1.0 - ratio)

    def _get_screen_position(self, x: int, y: int) -> (float, float):
        return (x + 1.5) * self.unit_size, (self.height - (y - 1.5) - 1) * self.unit_size

    # MARK: Drawing

    def _draw_map(self, walls: [[bool]]):
        for y, row in enumerate(walls):
            for x, is_there in enumerate(row):
                if is_there:
                    pos = self._get_screen_position(x, y)
                    self.graphics.draw_rect(
                        pos[0] - self.unit_size / 2,
                        pos[1] - self.unit_size / 2,
                        self.unit_size,
                        self.unit_size,
                        color="gray",
                        border="gray",
                        permanent=True
                    )

    def _draw_food(self, food: [[bool]]):
        for y, row in enumerate(food):
            for x, is_there in enumerate(row):
                if is_there:
                    self.graphics.draw_models(
                        self.unit_size / 6.0,
                        QUAD_MODEL,
                        [self._get_screen_position(x, y)],
                        colors=['white'],
                    )

    def _draw_info(self, score: int, pacman: Agent, ghosts: [Agent]):
        font = 'Arial 36 normal'

        self.graphics.draw_text(
            *self._get_screen_position(-1, -1),
            text=f'Score: {score}',
            font=font,
            color='white',
            anchor='nw'
        )
        position = self._get_screen_position(self.width, -1)
        for i, ghost in enumerate(reversed(ghosts)):
            distance = abs(ghost.position[0] - pacman.position[0]) + abs(ghost.position[1] - pacman.position[1])
            self.graphics.draw_text(
                position[0] - i * 80,
                position[1],
                text=f'{distance if ghost.alive else -1}',
                font=font,
                color=ghost.color,
                anchor='ne'
            )

    def _draw_pacman(self, pacman: Agent, dt: float):
        pacman_direction = pacman.direction
        pacman_mouth_angle = 40 + 20 * math.sin(time.time() * math.pi * 2 * PacmanGraphics.PACMAN_WAKAS_PER_SECOND)
        self.graphics.draw_arc(
            *self._animate_position(pacman, dt),
            self.unit_size / 2.4,
            angle=360 - pacman_mouth_angle,
            start_angle=(pacman_direction - 1) * 90 + pacman_mouth_angle / 2
        )

    def _draw_ghosts(self, ghosts: [Agent], dt: float):
        alive_ghosts = [g for g in ghosts if g.alive]
        ghost_positions = [self._animate_position(g, dt) for g in alive_ghosts]
        # Ghosts
        self.graphics.draw_models(
            self.unit_size / 2,
            GHOST_MODEL,
            ghost_positions,
            width=2.0,
            colors=[g.color for g in alive_ghosts],
            smooth=True
        )

        # Eyeballs
        self._draw_ghost_eyeball_parts(self.unit_size / 5, 'white', ghost_positions)

        # Irises
        iris_size = self.unit_size / 16
        self._draw_ghost_eyeball_parts(iris_size, 'black', [(
            pos[0] + Game.Moves[g.direction][0] * iris_size,
            pos[1] - Game.Moves[g.direction][1] * iris_size
        ) for g, pos in zip(ghosts, ghost_positions)])

    def _draw_ghost_eyeball_parts(self, size: float, color: str, positions: [(float, float)]):
        offset = self.unit_size / 8, self.unit_size / 8
        offset_positions = []

        for position in positions:
            offset_positions.append((position[0] - offset[0], position[1] - offset[1]))
            offset_positions.append((position[0] + offset[0], position[1] - offset[1]))

        self.graphics.draw_models(
            size,
            QUAD_MODEL,
            offset_positions,
            width=2.0,
            colors=[color for _ in offset_positions],
            smooth=True
        )
