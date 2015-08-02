__author__ = 'Conan'
import random

class State(object):
    def __init__(self, player=-999, dealer=-999):
        if player==-999:
            self.player = random.randint(1,10)
            self.dealer = random.randint(1,10)
            self.turn = 'player'
        else:
            self.player = player
            self.dealer = dealer
        self.gameover = 0

