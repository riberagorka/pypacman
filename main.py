
from cli import get_run_configuration

if __name__ == '__main__':
    app = None
    config = get_run_configuration()

    if config.frame_rate < 0:   # graphics disabled
        from game import Game
        app = Game(config.layout, config.pacman, config.ghost, config.n_ghosts)
    else:                       # graphics enabled
        from app import Application
        app = Application(config.layout, config.pacman, config.ghost, config.n_ghosts, config.frame_rate)

    for _ in range(config.n_games):
        app.run()
        app.reset()
