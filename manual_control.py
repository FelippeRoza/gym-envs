import gym
import grid_envs

def key_event(event):

    if event.key == 'up':
        action = 0
    elif event.key == 'down':
        action = 1
    elif event.key == 'left':
        action = 2
    elif event.key == 'right':
        action = 3
    else:
        print('invalid key, will go up')
        action = 0
    s_t, r_t, done, _ = env.step(action)
    print(s_t)
    if done:
        print('Done! Reward:', r_t)
        env.reset()

    env.render()

def on_close(event):
    print('Press [enter] to end')

env = gym.make("DynamicGridWorld-2-MovObs-7x7-Random-v0")
env.reset()

env.fig.canvas.mpl_connect('key_press_event', key_event)
env.fig.canvas.mpl_connect('close_event', on_close)
input("Press [enter] to continue.")
