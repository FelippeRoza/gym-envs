import pygame
import sys
import random
import time
import copy
import numpy as np
from copy import copy
import gym
from gym import spaces

BLACK =     (  0,   0,   0)
WHITE =     (250, 250, 250)
BLUE =      (  0,   0, 255)
GREEN =     (  0, 255,   0)
RED =       (255,   0,   0)
YELLOW =    (255, 255,   0)
BLOCKSIZE = 40
RENDER_FPS = 20

class AbstractMovingObject():
    '''
    docstring for abstract moving object on the grid,
    can be an actor or an obstacle
    '''
    def __init__(self, pos, grid_dims, radius=None):
        self.pos = pos
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
    
    def move(self, action):
        self._move(action)


class MovingObstacle(AbstractMovingObject):
    def __init__(self, color=BLACK, step_size=1, **kwargs):
        super().__init__(**kwargs)
        self.step_size = step_size
        self.color = color
    
    def move(self):
        for i in range(self.step_size):
            action = random.choice(range(len(self.action_dict)))
            self._move(action)


class StaticGoal():
    def __init__(self, pos, color=YELLOW):
        self.pos = pos
        self.color = color


class GridState():

    def __init__(self, grid_dims, obs_positions, agent_position, goal_position):
        self.grid_dims = grid_dims
        self.obs_positions = obs_positions 
        self.agent_position = agent_position
        self.goal_position = goal_position
        self.make_grid()

    def update(self, new_obs_positions, new_agent_position):
        self.obs_positions = new_obs_positions 
        self.agent_position = new_agent_position
        self.make_grid()

    def make_grid(self, one_hot=True):
        '''
        encoding: agent = 1, goal = 5, regular obstacle = 2
        '''
        if one_hot:
            grid = np.zeros((3, *self.grid_dims), dtype=np.int8)

            grid[(0, *self.agent_position)] = 1
            for obs_pos in self.obs_positions:
                grid[(1, *obs_pos)] = 1
            grid[(2, *self.goal_position)] = 1
            self.grid = grid
        else:
            grid = np.zeros(self.grid_dims, dtype=np.int8)
            grid[self.agent_position] = 1
            for obs_pos in self.obs_positions:
                grid[obs_pos] = 2
            grid[self.goal_position] = 3
            self.grid = grid


class DynamicGridWorld(gym.Env):
    '''
    docstring for GridWorld
    '''
    def __init__(self, grid_dims, agent_position, goal_position, obs_positions, obs_moving_radius=1):
     
        self.grid_dims = grid_dims
        self.n_rows, self.n_cols = grid_dims

        #init positions
        self.init_agent_position = agent_position
        self.init_obs_positions = obs_positions
        self.init_goal_position = goal_position
        self.obs_moving_radius = obs_moving_radius

        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.MultiBinary([3,self.n_rows,self.n_cols]) # one_hot encoded observations

        #for rendering
        self.screen = None
        
    def step(self, action):

        new_obs_positions = set()

        # move objects
        for obst in self.obstacles:
            obst.move()
            new_obs_positions.add(obst.pos)
           
        # move agent
        self.agent.move(action)
        new_agent_pos = self.agent.pos
        new_state = copy(self.state)
        new_state.update(new_obs_positions, new_agent_pos)

        if self.is_collision(self.state, new_state):
            reward = -1
            self.done = True

        elif self.is_goal(new_state):
            self.state = new_state
            reward = 1
            self.done = True

        else:
            self.state = new_state
            reward = 0
            self.done = False

        observation = self.state.grid
        info = {} #so far no info is returned

        return observation, reward, self.done, info

    def is_collision(self, old_state, new_state):
        if new_state.agent_position in new_state.obs_positions:
            print('Collision: same new state')
            return True 
        elif new_state.agent_position in old_state.obs_positions and old_state.agent_position in new_state.obs_positions:
            print('Collision: swapping is not allowed')
            return True
        else:
            return False
    
    def is_goal(self, new_state):
        return new_state.agent_position == new_state.goal_position

    def reset(self):
        agent_position, goal_position, obs_positions = self.init_agent_position, self.init_goal_position, self.init_obs_positions
        self.obstacles = [MovingObstacle(pos=pos, grid_dims=self.grid_dims, radius=self.obs_moving_radius) for pos in obs_positions]
        self.agent = MovingAgent(pos=agent_position, grid_dims=self.grid_dims)
        self.goal = StaticGoal(pos=goal_position)
        self.state = GridState(self.grid_dims, set(obs_positions), agent_position, goal_position)

        return self.state.grid

    def render(self, close=False):

        def drawGrid():
            for x in range(self.n_rows):
                for y in range(self.n_cols):
                    rect = pygame.Rect(x*BLOCKSIZE, y*BLOCKSIZE,
                                    BLOCKSIZE, BLOCKSIZE)
                    pygame.draw.rect(self.screen, BLACK, rect, 1)
   
        def drawObject(grid_object):
            
            def draw_circle(pos, color):
                center = (pos[1]*BLOCKSIZE+BLOCKSIZE/2, pos[0]*BLOCKSIZE+BLOCKSIZE/2)
                pygame.draw.circle(self.screen, color, center, BLOCKSIZE/2)

            def draw_rectangle(pos, color):
                rect = pygame.Rect(pos[1]*BLOCKSIZE, pos[0]*BLOCKSIZE, BLOCKSIZE,BLOCKSIZE)
                pygame.draw.rect(self.screen, color, rect)


            if isinstance(grid_object, MovingAgent):
                draw_circle(grid_object.pos, grid_object.color)

            elif isinstance(grid_object, MovingObstacle):
                draw_rectangle(grid_object.pos, grid_object.color)

            elif isinstance(grid_object, StaticGoal):
                draw_rectangle(grid_object.pos, grid_object.color)

        if close:
            print('closing')
            pygame.display.quit()
            pygame.quit()
            sys.exit()
            
        else:
            if self.screen is None:
                pygame.init()
                self.screen = pygame.display.set_mode((self.n_cols * BLOCKSIZE, self.n_rows * BLOCKSIZE))
                self.clock = pygame.time.Clock()

        self.screen.fill(WHITE)
        drawGrid()

        for grid_object in [*self.obstacles, self.agent, self.goal]:
            drawObject(grid_object)

        pygame.display.update()
        self.clock.tick(RENDER_FPS)

        
    def stop(self):
   
        pygame.display.quit()
        print('stopped display')
        pygame.quit()
        sys.exit()
        raise SystemExit
        



class DGW_2_MovObs_7x7_Random(DynamicGridWorld):
    def __init__(self):
        grid_dims = (7,7)
        super().__init__(grid_dims, *self.random_pos_init())

    def random_pos_init(self):
        starting_positions = [(1,1), (1,5), (5,1), (5,5)]
        starting_positions = random.sample(starting_positions,4)
        agent_position = starting_positions[0]
        goal_position = starting_positions[1]
        obs_positions = starting_positions[2:]
        return agent_position, goal_position, obs_positions

    def reset(self):
        agent_position, goal_position, obs_positions = self.random_pos_init()
        self.obstacles = [MovingObstacle(pos=pos, grid_dims=self.grid_dims, radius=self.obs_moving_radius) for pos in obs_positions]
        self.agent = MovingAgent(pos=agent_position, grid_dims=self.grid_dims)
        self.goal = StaticGoal(pos=goal_position)
        self.state = GridState(self.grid_dims, set(obs_positions), agent_position, goal_position)

        return self.state.grid