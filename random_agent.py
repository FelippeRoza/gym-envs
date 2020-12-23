import gym
import grid_envs
import time
import random 

env = gym.make("DynamicGridWorld-2-MovObs-7x7-Random-v0")
env.reset()

print(env.action_space)

agent_actions = [0,3]
done = False
try:
	while not done:

		s_t, r_t, done, _ = env.step(env.action_space.sample())
		print(s_t)
		env.render()

		if done:
			env.reset()
			done = False


except KeyboardInterrupt:
	env.stop()