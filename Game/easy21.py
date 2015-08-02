__author__ = 'Conan'

from random import random, randint
from State import State


# Black cards positive, red cards negative
def red():
    return randint(-10,-1)

def black():
    return randint(1, 10)

# Draw card: 1/3 red, 2/3 black
def draw():
    if (random() < 1.0/3.0): return red()
    return black()

# Bust score
def bust(score):
    if 0 < score < 22: return 0
    return 1

def step(state, action):
    # If hit:
    if action==1:
        state.player += draw()
        if bust(state.player)==1: state.gameover =  1

    # If stick:
    if action==0:
        state.turn = 'dealer'
        while 0 < state.dealer < 17:
            state.dealer += draw()
            if bust(state.dealer)==1: break
        state.gameover = 1

    # If gameover check winner and return reward -1, 0 or 1
    if state.gameover==1:
        if state.player > 21: return state,-1
        if state.dealer > 21: return state, 1
        if state.player < state.dealer: return state, -1
        if state.player > state.dealer: return state, 1
        if state.player==state.dealer: return state, 0
    else: return state, 0

def printstate(state):
    print "Turn: ", state.turn, ", Player: ", state.player, ", Dealer: ", state.dealer, ", Gameover: ", state.gameover
    return None

if __name__ == '__main__':

    # Initialise state, test: stick on first card a=0
    s = State()
    a = randint(0, 1)
    if a==0:
        print "\nStick on first card:"
    else:
        print "\nCertain-loss always hit:"
    printstate(s)
    while s.gameover==0:
        s, reward = step(s,a)
        printstate(s)
    print "Reward: ", reward