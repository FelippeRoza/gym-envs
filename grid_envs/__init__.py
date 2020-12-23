from gym.envs.registration import register

register(
    id='DynamicGridWorld-v0',
    entry_point='grid_envs.envs:DynamicGridWorld'
)

register(
    id='DynamicGridWorld-2-MovObs-7x7-Random-v0', 
    entry_point='grid_envs.envs:DGW_2_MovObs_7x7_Random'
)
