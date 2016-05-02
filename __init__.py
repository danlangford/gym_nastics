from gym.envs.registration import registry, register, make, spec

from blackjack import BlackjackEnv


register(
    id='Blackjack-v0',
    entry_point='gym_nastics:BlackjackEnv',
    timestep_limit=200,
    reward_threshold=21.0,
)
