import random
from abc import ABC, abstractmethod
from game import Direction, Game

__all__ = [
    'Agent',
    'StaticAgent',
    'RandomAgent',
    'KeyboardAgent',
    'DispersingAgent',
    'PathFindingAgent'
]

_agent_id = 0


class Agent(ABC):

    def __init__(self, name: str, position: (int, int)):
        self.name = name
        self.position = position
        self.direction = Direction.Stop
        self.alive = True
        self.color = None  # used by ghosts
        self.keyboard_direction = None  # used by keyboard agent
        self.previous_position = position  # used for animation
        global _agent_id
        self.id = _agent_id
        _agent_id += 1

    def initialize(self):
        pass

    @abstractmethod
    def choose_action(self, game: Game) -> int:
        pass

    def observe_state(self, game: Game):
        pass


class StaticAgent(Agent):
    def choose_action(self, game: Game) -> int:
        return Direction.Stop


class RandomAgent(Agent):
    def choose_action(self, game: Game) -> int:
        return random.randint(1, 5)


class KeyboardAgent(Agent):
    def choose_action(self, game: Game) -> int:
        if self.keyboard_direction in game.get_pacman_legal_actions():
            return self.keyboard_direction
        return self.direction


class DispersingAgent(Agent):
    def choose_action(self, game: Game) -> int:
        other_ghosts = [g for g in game.ghosts if self.id != g.id]

        distances = []
        opposite_directions = []

        for g in other_ghosts:
            diff = g.position[0] - self.position[0], g.position[1] - self.position[1]

            distances.append(diff[0] ** 2 + diff[1] ** 2)

            opposite_direction = \
                -diff[0] / max(1, abs(diff[0])) * (abs(diff[0]) > abs(diff[1])), \
                -diff[1] / max(1, abs(diff[1])) * (abs(diff[0]) <= abs(diff[1]))

            opposite_directions.append(Direction.from_offset(*opposite_direction))

        total_distance = sum(distances)
        return random.choices(opposite_directions, [d / total_distance for d in distances])[0]


class PathFindingAgent(Agent):

    def get_distance(self, lhs: (int, int), rhs: (int, int)) -> int:
        return (rhs[0] - lhs[0]) ** 2 + (rhs[1] - lhs[1]) ** 2

    @abstractmethod
    def find_path(self, maze: [[bool]], start: (int, int), target: (int, int)) -> [(int, int)]:
        raise NotImplementedError

    def choose_action(self, game: Game):
        position = game.pacman.position

        target_position = get_closest_living_ghost_position(game.pacman, game.ghosts, self.get_distance)

        if target_position == (-1, -1) or target_position == position:
            return Direction.Stop

        path = self.find_path(game.map.walls, position, target_position)

        # Use first path point to calculate move direction
        return Direction.from_offset(path[1][0] - position[0], path[1][1] - position[1])


# MARK: Helper functions

def get_closest_living_ghost_position(pacman: Agent, ghosts: [Agent], get_distance):
    living_ghost_positions = [g.position for g in ghosts if g.alive]

    closest, min_distance = (-1, -1), 1000000000000
    d = []
    for i, position in enumerate(living_ghost_positions):
        distance = get_distance(pacman.position, position)
        d.append(distance)
        if distance < min_distance:
            min_distance = distance
            closest = position
    # print(min_distance, d)
    return closest
