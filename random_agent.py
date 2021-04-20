import gym
import grid_envs
import time
import random

env = gym.make("DynamicGridWorld-2-MovObs-7x7-Random-v0")

print(env.action_space.sample())

obs = env.reset()
env.render()
for i in range(1000):
    obs, reward, done, info = env.step(env.action_space.sample())

    if done:
      obs = env.reset()

    env.render()
    time.sleep(0.3)

env.close()
