import argparse
import importlib
import random
from typing import Type
import agent

__all__ = ['get_run_configuration', 'load_layout']


class Configuration:
    def __init__(self,
                 layout: [str],
                 pacman: Type[agent.Agent],
                 ghost: Type[agent.Agent],
                 n_games: int,
                 n_ghosts: int,
                 frame_rate: float):

        self.layout = layout
        self.pacman = pacman
        self.ghost = ghost
        self.n_games = n_games
        self.n_ghosts = n_ghosts
        self.frame_rate = frame_rate


def add_arguments(parser: argparse.ArgumentParser):
    parser.add_argument('-a', '--agent', default='agent.py',
                        dest='agent_module',
                        help='the name of the file from which to load custom agent classes')
    parser.add_argument('-r', '--frame-rate',  type=int, default=-2,  # default is -2 for compatibility reasons
                        dest='frame_rate',
                        help='Frames per second (0: unlimited, -1: no graphics')
    parser.add_argument('-s', '--seed', type=int, default=-1,
                        dest='seed',
                        help='Seed for random number generator')


def add_compatibility_arguments(parser: argparse.ArgumentParser):
    parser.add_argument('-n', '--numGames',  type=int, default=1,
                        dest='n_games',
                        help='the number of GAMES to play')
    parser.add_argument('-l', '--layout',  default='oneHunt',
                        dest='layout',
                        help='the name of the file from which to load the map layout')
    parser.add_argument('-p', '--pacman',  default='KeyboardAgent',
                        dest='pacman',
                        help='the type of Agent to be used for pacman')
    parser.add_argument('-g', '--ghosts',  default='StaticAgent',
                        dest='ghost',
                        help='the ghost agent TYPE in the ghostAgents module to use')
    parser.add_argument('-q', '--quietTextGraphics', action='store_true',
                        dest='no_graphics',
                        help='Run with no graphics (very fast)')
    parser.add_argument('-k', '--numghosts', type=int,  default=4,
                        dest='n_ghosts',
                        help='The maximum number of ghosts to use')
    parser.add_argument('-z', '--zoom', type=float,  default=1.0,
                        dest='zoom',
                        help='Zoom the size of the graphics window')
    parser.add_argument('-f', '--fixRandomSeed', action='store_true',
                        dest='fixed_seed',
                        help='Fixes the random seed to always play the same game')
    parser.add_argument('-t', '--frameTime',  type=float, default=0.1,
                        dest='frame_time',
                        help='Time to delay between frames; <0 means keyboard')


def get_run_configuration() -> Configuration:
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    add_compatibility_arguments(parser)
    args = parser.parse_args()

    if args.fixed_seed:
        random.seed(13375339)
    elif args.seed > -1:
        random.seed(args.seed)

    pacman, ghost = _load_pacman_and_ghost_from_module(
        args.agent_module.replace('.py', ''), args.pacman, args.ghost)

    frame_time = 0.0 if args.frame_time < 0.001 else 1.0 / args.frame_time
    frame_rate = args.frame_rate if args.no_graphics or args.frame_rate != -2 else frame_time

    return Configuration(
        load_layout(args.layout),
        pacman,
        ghost,
        args.n_games,
        args.n_ghosts,
        frame_rate
    )


def load_layout(name: str) -> [str]:
    return _load_layout_from_disk('layouts/' + name + '.lay')


def _load_layout_from_disk(path: str) -> [str]:
    data = []
    with open(path) as f:
        data.extend(f.read().splitlines())
    return data


def _load_pacman_and_ghost_from_module(module_name: str, pacman: str, ghost: str) -> (Type[agent.Agent], Type[agent.Agent]):
    module = importlib.import_module(module_name)
    return \
        module.__dict__.get(pacman, agent.__dict__.get(pacman, agent.KeyboardAgent)), \
        module.__dict__.get(ghost, agent.__dict__.get(ghost, agent.StaticAgent))
