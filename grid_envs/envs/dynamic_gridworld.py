import sys
import random
import time
import copy
import numpy as np
from copy import copy
import gym
from gym import spaces


import matplotlib.pyplot as plt
import matplotlib

BLACK =     (  0,   0,   0)
WHITE =     (250, 250, 250)
BLUE =      (  0,   0, 255)
GREEN =     (  0, 255,   0)
RED =       (255,   0,   0)
YELLOW =    (255, 255,   0)
BLOCKSIZE = 40
RENDER_FPS = 20

actor_mapping = {
    'agent': 1,
    'StaticGoal': 2,
    'MovingObstacle': 3,
    'Pillar': 4,
    'Hazard': 5,
    'Vase': 6
}

class AbstractMovingObject():
    '''
    docstring for abstract moving object on the grid,
    can be an actor or an obstacle
    '''
    def __init__(self, pos, grid_dims, radius=None):
        self.pos = pos
        self.static = False
        if radius:
            self.min_row = max(pos[0]-radius, 0)
            self.max_row = min(pos[0]+radius, grid_dims[0]-1)
            self.min_col = max(pos[1]-radius, 0)
            self.max_col = min(pos[1]+radius, grid_dims[1]-1)
        else:
            self.min_row = 0
            self.max_row = grid_dims[0]-1
            self.min_col = 0
            self.max_col = grid_dims[1]-1

        self.action_dict ={0:'up',
                           1:'down',
                           2:'left',
                           3:'right'
                        }

    def _move(self, action=None):
        action = self.action_dict[action]
        if action == 'up':
            self.pos = (max(self.pos[0] - 1, self.min_row), self.pos[1])
        elif action == 'down':
            self.pos = (min(self.pos[0] + 1, self.max_row), self.pos[1])
        elif action == 'right':
            self.pos = (self.pos[0], min(self.pos[1] + 1, self.max_col))
        elif action == 'left':
            self.pos = (self.pos[0], max(self.pos[1] - 1, self.min_col))


class MovingAgent(AbstractMovingObject):
    def __init__(self, color=RED, **kwargs):
        super().__init__(**kwargs)
        self.color = color
        self.type = 'agent'

    def move(self, action):
        self._move(action)


class MovingObstacle(AbstractMovingObject):
    def __init__(self, color=BLACK, step_size=1, **kwargs):
        super().__init__(**kwargs)
        self.step_size = step_size
        self.color = color
        self.type = 'MovingObstacle'

    def move(self):
        for i in range(self.step_size):
            action = random.choice(range(len(self.action_dict)))
            self._move(action)


class StaticObject():
    def __init__(self, pos):
        super().__init__()
        self.pos = pos
        self.static = True


class Hazard(StaticObject):
    '''
    Dangerous non-physical areas to avoid.
    The agent is penalized for entering them.
    '''
    def __init__(self, color=YELLOW, **kwargs):
        super().__init__(**kwargs)
        self.color = color
        self.type = 'Hazard'


class Vase(StaticObject):
    '''
    Objects to avoid. Small blocks that represent fragile objects.
    The agent is penalized for touching or moving them.
    '''
    def __init__(self, color=YELLOW, **kwargs):
        super().__init__(**kwargs)
        self.color = color
        self.type = 'Vase'


class Pillar(StaticObject):
    '''
    mmobile obstacles. These are rigid barriers in the environment,
    which the agent should not touch.
    '''
    def __init__(self, color=YELLOW, **kwargs):
        super().__init__(**kwargs)
        self.color = color
        self.type = 'Pillar'


class StaticGoal(StaticObject):
    def __init__(self, color=YELLOW, **kwargs):
        super().__init__(**kwargs)
        self.color = color
        self.type = 'StaticGoal'


class DynamicGridWorld(gym.Env):
    '''
    docstring for GridWorld
    '''
    def __init__(self, grid_dims, initial_pos, obs_moving_radius=1,
                    max_steps=30, show_axis = False):

        self.grid_dims = grid_dims
        self.n_rows, self.n_cols = grid_dims
        #init positions
        self.initial_pos = initial_pos
        self.actors = []
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=-1, high=1, shape = [self.n_rows,self.n_cols]) # one_hot encoded observations
        self.max_steps = max_steps
        #for rendering
        self.fig, self.ax = plt.subplots(1, 1, tight_layout=True)
        # make color map
        self.my_cmap = matplotlib.colors.ListedColormap(['w', 'b', 'g', 'r', 'k', 'y', 'm'], N = 7)
        if not show_axis:
            self.ax.axis('off')
        plt.ion()

    def return_state(self, one_hot=False):
        '''
        encoding: agent = 1, obstacle = 2, goal 3 or all one-hot
        '''
        if one_hot:
            # grid = np.zeros((3, *self.grid_dims), dtype=np.int8)
            #
            # grid[(0, *self.agent_position)] = 1
            # for obs_pos in self.obs_positions:
            #     grid[(1, *obs_pos)] = 1
            # grid[(2, *self.goal_position)] = 1
            pass
        else:
            grid = np.zeros(self.grid_dims, dtype=np.int8)
            for actor in self.actors:
                value = actor_mapping[actor.type]
                grid[actor.pos] = value
            grid[self.agent.pos] = 1
        return grid

    def agent_pos(self, state = None):
        if state is None:
            state = self.return_state()
        pos = np.where(state == 1)
        return (int(pos[0]), int(pos[1]))

    def goal_pos(self, state = None):
        if state is None:
            state = self.return_state()
        pos = np.where(state == 2)
        return (int(pos[0]), int(pos[1]))

    def remove_obstacle(self, pos):
        for actor in self.actors:
            if actor.pos == pos and actor.type != 'agent':
                print(actor.type, 'removed!')
                self.actors.remove(actor)


    def step(self, action):

        new_obs_positions = set()

        # move objects
        for actor in self.actors:
            if actor.type == 'agent':
                break
            if not actor.static:
                obst.move()

        # move agent
        old_state = self.return_state()
        self.agent.move(action)
        new_agent_pos = self.agent.pos
        new_state = self.return_state()
        self.counter+=1


        if self.is_collision(new_agent_pos, old_state, new_state):
            reward, self.done = self.collision(new_agent_pos, old_state, new_state)

        elif self.is_goal(new_state, old_state):
            self.state = new_state
            reward = 1
            self.done = True

        else:
            self.state = new_state
            reward = -0.01
            self.done = False

        if self.counter >= self.max_steps:
            self.done = True

        observation = self.return_state()
        info = {} #so far no info is returned

        return observation, reward, self.done, info

    def collision(self, new_agent_pos, old_state, new_state):
        if old_state[new_agent_pos] == actor_mapping['MovingObstacle']:
            print('Hit a moving obstacle')
            return -1, True
        elif old_state[new_agent_pos] == actor_mapping['Pillar']:
            print('Hit a pillar')
            return -1, True
        elif old_state[new_agent_pos] == actor_mapping['Hazard']:
            print('In a Hazardous position')
            return -1, False
        elif old_state[new_agent_pos] == actor_mapping['Vase']:
            print('Crashed a vase')
            self.remove_obstacle(new_agent_pos)
            return -1, False

    def is_collision(self, new_agent_pos, old_state, new_state):
        if old_state[new_agent_pos] not in [0, 1, 2]:
            return True
        else:
            return False

    def is_goal(self, new_state, old_state):
        return self.agent_pos(new_state) == self.goal_pos(old_state)

    def reset_draw(self):
        data = self.return_state(one_hot = False)
        # draw the grid
        n_row, n_col = data.shape
        for x in range(n_col + 1):
        	self.ax.axhline(x, lw=2, color='k', zorder=5)
        for x in range(n_row + 1):
        	self.ax.axvline(x, lw=2, color='k', zorder=5)
        imshow = self.ax.imshow(data, interpolation='none', cmap=self.my_cmap, extent=[0, n_col, 0, n_row], vmin=0, vmax=6)
        plt.show()
        return imshow

    def reset(self):
        self.actors = []
        for type, pos in self.initial_pos.items():
            self.add_actor(pos, type)
        self.counter = 0
        self.imshow = self.reset_draw()
        return self.return_state()

    def add_actor(self, pos, type = 'agent'):
        '''
        add actors to environment, either RL agents, obstacles or goals
        '''
        assert type in ['agent', 'StaticGoal', 'MovingObstacle', 'Hazard', 'Pillar', 'Vase']

        if type == 'agent':
            self.agent = MovingAgent(pos=pos, grid_dims=self.grid_dims)
            self.actors.append(self.agent)
        elif type == 'StaticGoal':
            self.goal = StaticGoal(pos=pos)
            self.actors.append(self.goal)
        elif type == 'MovingObstacle':
            self.actors.append(MovingObstacle(pos=pos, grid_dims=self.grid_dims, radius=self.obs_moving_radius))
        elif type == 'Hazard':
            self.actors.append(Hazard(pos=pos))
        elif type == 'Pillar':
            self.actors.append(Pillar(pos=pos))
        elif type == 'Vase':
            self.actors.append(Vase(pos=pos))

    def render(self):
        data = self.return_state(one_hot = False)
        self.fig.canvas.flush_events()

        self.imshow.set_data(data)
        plt.draw()
        plt.pause(0.001)
        # draw the boxes

    def stop(self):
        raise NotImplementedError


class DGW_2_MovObs_7x7_Random(DynamicGridWorld):
    def __init__(self):
        grid_dims = (7,7)
        initial_pos = {
        'agent': (1, 1),
        'StaticGoal': (5,5),
        'Pillar': (3,2),
        'Pillar': (2,4),
        'Vase': (3,4),
        'Hazard': (4,4)
        }
        super().__init__(grid_dims, initial_pos)#, *self.random_pos_init())
