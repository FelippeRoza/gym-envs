import pygame
import sys
import random
import time

BLACK =     (  0,   0,   0)
WHITE =     (250, 250, 250)
BLUE =      (  0,   0, 255)
GREEN =     (  0, 255,   0)
RED =       (255,   0,   0)


class actor(object):
    """docstring for actor"""
    def __init__(self, blocksize = 40, HEIGHT = 10, WIDTH = 10, x0 = 0, y0 = 0, step_size = 1, actor_type = 'obstacle'):
        super(actor, self).__init__()
        self.x = x0
        self.y = y0
        self.h = HEIGHT
        self.w = WIDTH
        self.step_size = step_size # how many tiles it moves each tick
        self.blocksize = blocksize
        self.type = actor_type

    def move(self):
        options = ['up', 'down', 'right', 'left']
        action = random.choice(options)

        if action == 'up':
            self.y = min(self.y + self.step_size, self.h - 1)
        elif action == 'down':
            self.y = max(self.y - self.step_size, 0) # avoid negative coordinate
        elif action == 'right':
            self.x = min(self.x + self.step_size, self.w - 1)
        else:
            self.x = max(self.x - self.step_size, 0)
        print('coordinate: ', self.x, self.y)

    def draw(self, screen):
        pos = (self.x * self.blocksize + self.blocksize/2, self.y * self.blocksize + self.blocksize/2)
        if self.type == 'obstacle':
            color = RED
        elif self.type == 'agent':
            color = BLUE
        elif self.type == 'goal':
            color = GREEN
        pygame.draw.circle(screen, color, pos, self.blocksize / 2)


class gridWorld(object):
    """docstring for gridWorld"""
    def __init__(self, HEIGHT = 10, WIDTH = 10, blocksize = 40):
        super(gridWorld, self).__init__()
        
        self.h = HEIGHT # number of vertical blocks
        self.w = WIDTH  # number of horizontal blocks
        self.blocksize = blocksize # size of the grid block

        pygame.init()
        self.screen = pygame.display.set_mode((self.w * self.blocksize, self.h * self.blocksize))
        self.clock = pygame.time.Clock()
        self.goal = actor(x0 = 5, y0 = 5, step_size = 0, actor_type = 'goal')
        self.obstacle = actor(x0 = 5, y0 = 5)
        self.agent = actor(x0 = 0, y0 = HEIGHT - 1, actor_type = 'agent')
        self.run = True
        self.loop()

    def loop(self):

        while(self.run):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
            self.screen.fill(WHITE)
            self.drawGrid()
            self.tick()
            pygame.display.flip()

        self.quit()

    def quit(self):
        pygame.display.quit()
        pygame.quit()
        sys.exit()

    def collision(self):
        if (self.agent.x == self.obstacle.x) and (self.agent.y == self.obstacle.y):
            self.run = False
            print('Collision has happened')
        print('agent:', (self.agent.x, self.agent.y), 'obstacle:', (self.obstacle.x, self.obstacle.y))


    def tick(self):
        for actor in [self.obstacle, self.agent, self.goal]:
            actor.move()
            actor.draw(self.screen)
        self.collision()
        time.sleep(0.5)


    def drawGrid(self):
        for x in range(self.h):
            for y in range(self.w):
                rect = pygame.Rect(x*self.blocksize, y*self.blocksize,
                                   self.blocksize, self.blocksize)
                pygame.draw.rect(self.screen, BLACK, rect, 1)



if __name__ == "__main__":
    
    game = gridWorld()
