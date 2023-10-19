from gym.envs.registration import register

register(
    id='gym_customizedEnv-v0',
    entry_point='gym_customizedEnv.envs:CustomizedEnv',
    #max_episode_steps=2000,
)
