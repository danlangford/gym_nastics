from __future__ import print_function
from blackjack import BlackjackEnv

# Support python 2 and 3
try:
    input = raw_input
except NameError:
    pass

bjenv = BlackjackEnv()


def play_game():
    obs = bjenv.reset()
    bjenv.render()

    total_reward = 0
    done = False
    while not done:
        action = -1
        hmn_in = input("[H]it, [S]tand or e[X]it? >")
        if hmn_in in ['H', 'h']:
            action = 0
        elif hmn_in in ['S', 's']:
            action = 1
        elif hmn_in in ['X', 'x']:
            print('bye')
            exit()
        else:
            continue

        obs, reward, done, info = bjenv.step(action)
        total_reward += reward
        bjenv.render()
        if done:
            print('Reward:{}'.format(reward))


def main():
    play_game()
    if input("Play again? [Y]es/[N]o >") in ['Y', 'y']:
        main()
    print('EOF')


if __name__ == "__main__":
    main()
