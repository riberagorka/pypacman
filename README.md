# pypacman
Small pacman game written in standard Python 3.7.

## Run
To run the game, execute main.py:

```shell
python main.py
```

To see the list of command-line arguments that main.py accepts:

```shell
python main.py --help
```


## Custom Agents
To choose a different agent for pacman or for a ghost, specify the name of the agent class in the argument:
```shell
python main.py -p KeyboardAgent -g StaticAgent
```

To use your own agent there are 2 steps:
1. Define your own custom agent by overriding the choose_action(self, game) method of the Agent class
```python
# my_agent.py
from agent import Agent, Direction, Game

class MyAgent(Agent):
    def choose_action(self, game: Game):
        return Direction.Stop
```
2. Specify the name of the file where your custom agent is defined (using the -a argument):
Make sure the file is in the same directory as the main script.
```shell
python main.py -p MyAgent -a my_agent.py
```

## Initialization and observing game state
In your custom agent, you can override the initialize(self) method to do something when the agent is created.
You can also override the observe_state(self, game) method to do something after each action.
These might be useful to for example open a file, and write information about the game to the file after each action.

```python
# my_agent.py
from agent import Agent, Direction, Game

class MyAgent(Agent):
    def initialize(self):
        print('created agent')
    
    def choose_action(self, game: Game):
        return Direction.Stop
        
    def observe_state(self, game: Game):
        print('observing state')
    
```

```shell
python main.py -p MyAgent -a my_agent.py
```
