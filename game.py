

__all__ = ['Direction', 'Game']

GHOST_COLORS = ['red', 'green', 'blue', 'orange']


class Direction:
    North = 2
    South = 4
    East = 1
    West = 3
    Stop = 5

    Names = ['North', 'South', 'East', 'West', 'Stop']

    Offsets = {
        (0, 0): Stop,
        (0, 1): North,
        (0, -1): South,
        (1, 0): East,
        (-1, 0): West
    }

    @staticmethod
    def to_string(direction: int):
        assert 0 < direction < 4, f'{direction} is not a valid direction (1-5)'
        return Direction.Names[direction - 1]

    @staticmethod
    def from_string(direction: str):
        return Direction.Names.index(direction)

    @staticmethod
    def from_offset(x: int, y: int):
        return Direction.Offsets[(x, y)]

    @staticmethod
    def is_opposite(d1: int, d2: int) -> bool:
        return d1 == Direction.North and d2 == Direction.South or \
               d1 == Direction.South and d2 == Direction.North or \
               d1 == Direction.East and d2 == Direction.West or \
               d1 == Direction.West and d2 == Direction.East


class Flags:
    Space = 0x00
    Wall = 0x01
    Food = 0x02
    Pacman = 0x04
    Ghost = 0x08


class Map:

    Square = {
        ' ': Flags.Space,
        '%': Flags.Wall,
        '.': Flags.Food,
        'P': Flags.Pacman,
        'G': Flags.Ghost,

        'space': Flags.Space,
        'wall': Flags.Wall,
        'food': Flags.Food,
        'pacman': Flags.Pacman,
        'ghost': Flags.Ghost,
    }

    def __init__(self, layout: [str]):
        self.layout = layout
        self.map = [[0 for _ in range(len(layout[0]))] for _ in range(len(layout))]
        self.food = [[False for _ in range(len(layout[0]))] for _ in range(len(layout))]
        self.walls = [[False for _ in range(len(layout[0]))] for _ in range(len(layout))]
        self.pacman_initial_position = 0, 0
        self.ghost_initial_positions = []
        self._parse_map(layout)
        self.initial_food = [[v for v in row] for row in self.food]
        self.width = len(self.map[0])
        self.height = len(self.map)

    def add(self, flag: int, x: int, y: int):
        self.map[y][x] |= flag
        if (flag & Flags.Food) > 0:
            self.food[y][x] = True

    def remove(self, flag: int, x: int, y: int):
        self.map[y][x] &= ~flag
        if (flag & Flags.Food) > 0:
            self.food[y][x] = False

    def is_at(self, flag: int, x: int, y: int):
        return (self.map[y][x] & flag) > 0

    def reset(self):
        self.food = [[v for v in row] for row in self.initial_food]
        for y, row in enumerate(self.food):
            for x, is_there in enumerate(row):
                self.add(Flags.Food * is_there, x, y)

        self.add(Flags.Pacman, *self.pacman_initial_position)
        for pos in self.ghost_initial_positions:
            self.add(Flags.Ghost, *pos)

    def _parse_map(self, layout: [str]):
        for y, row in enumerate(reversed(layout)):
            for x, square in enumerate(row):
                self.map[y][x] |= Map.Square.get(square, 0)
                self.food[y][x] = square == '.'
                self.walls[y][x] = square == '%'
                if square == 'P':
                    self.pacman_initial_position = x, y
                elif square == 'G':
                    self.ghost_initial_positions.append((x, y))


class Game:

    SCORE_PER_FOOD = 10
    SCORE_PER_GHOST = 100

    Moves = {
        Direction.North: (0, 1),
        Direction.South: (0, -1),
        Direction.East: (1, 0),
        Direction.West: (-1, 0),
        Direction.Stop: (0, 0)
    }

    def __init__(self, layout: [str], pacman, ghost, n_ghosts: int):
        self.score = 0
        self.map = Map(layout)
        self.pacman = pacman('pacman', self.map.pacman_initial_position)
        self.ghosts = [ghost('ghost', pos) for pos, _ in zip(self.map.ghost_initial_positions, range(n_ghosts))]
        for ghost, color in zip(self.ghosts, GHOST_COLORS):
            ghost.color = color

        for agent in self.ghosts + [self.pacman]:
            agent.initialize()

    def get_pacman_legal_actions(self) -> [int]:
        return self.get_legal_actions(self.pacman)

    def get_legal_actions(self, agent) -> [int]:
        legal = []

        for direction in range(1, 5):

            position = agent.position[0] + Game.Moves[direction][0],\
                       agent.position[1] + Game.Moves[direction][1]

            if not self.map.is_at(Flags.Wall, *position) \
                    and (not self.map.is_at(Flags.Ghost, *position) or agent.name == 'pacman'):
                legal.append(direction)

        return legal

    def is_running(self):
        return any(g.alive for g in self.ghosts)

    def reset(self):
        self.map.reset()
        self.score = 0
        self.pacman.position = self.map.pacman_initial_position
        for ghost, position in zip(self.ghosts, self.map.ghost_initial_positions):
            ghost.alive = True
            ghost.position = position

        for agent in self.ghosts + [self.pacman]:
            agent.initialize()

    def run(self):
        while self.is_running():
            self.update()

    def update(self):
        self.score -= 1

        for agent in self.ghosts + [self.pacman]:

            if not agent.alive:
                continue

            position = agent.position
            direction = agent.choose_action(self)
            agent.previous_position = position

            if direction in self.get_legal_actions(agent):

                offset = Game.Moves[direction]
                agent.position = (position[0] + offset[0], position[1] + offset[1])
                agent.direction = direction

                self.map.remove(Map.Square[agent.name], *position)
                self.map.add(Map.Square[agent.name], *agent.position)

                if agent.name == 'pacman' or Direction.is_opposite(self.pacman.direction, agent.direction):
                    self._update_map_and_score()

                agent.observe_state(self)

    # MARK: Private

    def _update_map_and_score(self):
        # pacman eats food
        if self.map.is_at(Flags.Food, *self.pacman.position):
            self.map.remove(Flags.Food, *self.pacman.position)
            self.score += Game.SCORE_PER_FOOD

        # pacman eats a ghost
        if self.map.is_at(Flags.Ghost, *self.pacman.position):
            self.map.remove(Flags.Ghost, *self.pacman.position)
            self.score += Game.SCORE_PER_GHOST
            for g in self.ghosts:
                if g.alive and g.position == self.pacman.position:
                    g.alive = False
                    g.position = -1000, -1000
