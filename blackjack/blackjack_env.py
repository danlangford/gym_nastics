import sys
import pydealer
import gym
from gym import spaces
from six import StringIO


class BlackjackEnv(gym.Env):
    """
    Simple blackjack environment

    supports actions Hit (0) and Stand (1)
    observation is Tuple(Discrete(11),Discrete(11))
    you are only awarded your points when done==True
    your points will be the score of your cards if you beat the dealer and didnt bust
    the opening player hand will never be a blackjack, those hands require no decisions

    Splitting and Betting are not supported (yet?)
    """

    metadata = {'render.modes': ['human', 'ansi']}

    def __init__(self):
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Tuple([spaces.Discrete(11), spaces.Discrete(11)])
        self.card_repr = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
                          'Jack': 'J', 'Queen': 'Q', 'King': 'K', 'Ace': 'A'}
        self.card_vals = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
                          'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 1}

    def _reset(self):
        self.lastaction = None
        self.deck = pydealer.Deck()
        self.deck.shuffle()

        self.player_hand = pydealer.Stack()
        self.dealer_hand = pydealer.Stack()

        self.player_hand += self.deck.deal(1)
        self.dealer_hand += self.deck.deal(1)
        self.player_hand += self.deck.deal(1)

        if self.score(self.player_hand) == 21 or self.score(self.dealer_hand) == 21:
            self._reset()

        return self.obs()

    def _step(self, action):
        assert (action in [0, 1])
        self.lastaction = action
        done = False
        reward = 0
        p_score = self.score(self.player_hand)
        d_score = self.score(self.dealer_hand)

        if action == 0:
            # Player HIT
            self.player_hand += self.deck.deal(1)
            p_score = self.score(self.player_hand)
            done = (p_score >= 21)
            if p_score == 21:
                reward = p_score

        elif action == 1:
            # Player STAND
            self.dealer_hand += self.deck.deal(1)
            d_score = self.score(self.dealer_hand)
            while d_score <= 16:
                # dealer must hit at 16 or below
                self.dealer_hand += self.deck.deal(1)
                d_score = self.score(self.dealer_hand)
            if d_score < p_score <= 21:
                reward = p_score
            elif p_score < d_score > 21:
                reward = p_score
            done = True

        return self.obs(), reward, done, \
               {'player_score': self.score(self.player_hand, 'display'),
                'dealer_score': self.score(self.dealer_hand, 'display')}

    def _render(self, mode='human', close=False):
        if close:
            return

        outfile = StringIO() if mode == 'ansi' else sys.stdout

        outfile.write('Player Hand ({}): {}\nDealer Hand ({}): {}\n'.format(
            self.score(self.player_hand, mode='display'),
            [self.card_repr[d.value] for d in self.player_hand],
            self.score(self.dealer_hand, mode='display'),
            [self.card_repr[p.value] for p in self.dealer_hand]))
        if self.lastaction is not None:
            outfile.write('Last Action: {}\n'.format(['Hit', 'Stand'][self.lastaction]))
        else:
            outfile.write('\n')

        return outfile

    def obs(self):
        obs = ([self.card_repr[d.value] for d in self.player_hand],
               [self.card_repr[p.value] for p in self.dealer_hand])
        return obs

    def score(self, hand, mode='auto'):
        score = sum(self.card_vals[i.value] for i in hand)

        if mode == 'display':
            if len(hand.find('Ace')) >= 1:
                score = '{}/{}'.format(self.score(hand, 'soft'), self.score(hand, 'hard'))
            else:
                score = '{}'.format(self.score(hand, 'soft'))

        elif mode == 'auto':
            if score <= 11 and len(hand.find('Ace')) >= 1:
                score += 10
        elif mode == 'hard':
            if len(hand.find('Ace')) >= 1:
                score += 10
        elif mode == 'soft':
            score = score

        return score
