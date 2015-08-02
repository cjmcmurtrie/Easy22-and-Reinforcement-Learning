__author__ = 'Conan'

from State import State
from easy21 import step
from easy21_TDLearning import plot, epsilon
from numpy import arange as frange
from collections import defaultdict
from random import random, randint
from itertools import product
import pickle


playercuboid = [range(1, 7), range(4, 10), range(7, 13), range(10, 16), range(13, 19), range(16, 22)]
dealercuboid = [range(1, 5), range(4, 8), range(7, 11)]


def update(actionvalue, features, action, parameters):
    actionvalue[(tuple(features), action)] = sum([x[0]*x[1] for x in zip(features, parameters)])
    return actionvalue


def mse(MCactionvalue, actionvalue):
    player = range(1,22)
    dealer = range(1,11)
    action = [0, 1]
    errors = []
    for p, d, a in product(player, dealer, action):
        state = State(p, d)
        features = linear(state)
        errors += [(actionvalue[(tuple(features), a)] - MCactionvalue[(p, d, a)])**2]
    return sum(errors)


def greedy(state, actionvalue, e):
    hit = actionvalue[(tuple(state),1)]
    stick = actionvalue[(tuple(state),0)]
    if random() > e and hit != stick:
        if hit < stick: return 0
        if hit > stick: return 1
    else:
        if random() < 0.7: return 1
        return 0


def linear(state):
    dealerfeatures = []; playerfeatures = []
    for p in range(len(playercuboid)):
        if state.player in playercuboid[p]: playerfeatures += [1]
        else: playerfeatures += [0]
    for d in range(len(dealercuboid)):
        if state.dealer in dealercuboid[d]: dealerfeatures += [1]
        else: dealerfeatures += [0]
    features = [0.0]*(3*6)
    for f in range(len(features)):
        d = int(f / len(playercuboid))
        p = int(f % len(playercuboid))
        features[f] = dealerfeatures[d] * playerfeatures[p]
    return features


if __name__ == '__main__':

    iterations = 1000
    lambdas = frange(0.0,1.1,0.1)
    meansquarerror = []
    MCactionvalue = pickle.load(open('MonteCarloActionValueTrial.p', 'rb'))

    for lamBda in lambdas:
        print "Lambda ", lamBda

        actionvalue = defaultdict(float)

        features, hitparam, stickparam = [0.0]*(3*6), [0.0]*(3*6), [0.0]*(3*6)
        e = 0.05
        a = 0.01
        mses = []

        for game in range(iterations):

            if lamBda in (0.0, 1.0): mses += [(game, mse(MCactionvalue, actionvalue))]
            hiteligible, stickeligible = [0.0]*(3*6), [0.0]*(3*6)
            state = State()
            features = linear(state)

            action = greedy(features, actionvalue, e)

            while state.gameover==0:

                if action==1: hiteligible = [sum(x) for x in zip(hiteligible, features)]
                else: stickeligible = [sum(x) for x in zip(stickeligible, features)]

                state, reward = step(state, action)
                features = linear(state)

                hitdelta = reward - sum([x[0]*x[1] for x in zip(features, hitparam)])
                stickdelta = reward - sum([x[0]*x[1] for x in zip(features, stickparam)])

                if action==1:
                    actionvalue = update(actionvalue, features, action, hitparam)
                    hitdelta += actionvalue[(tuple(features), 1)]
                else:
                    actionvalue = update(actionvalue, features, action, stickparam)
                    stickdelta += actionvalue[(tuple(features), 0)]

                hitparam = [sum(x) for x in zip(hitparam, [a * hitdelta * h for h in hiteligible])]
                stickparam = [sum(x) for x in zip(stickparam, [a * stickdelta * s for s in stickeligible])]

                hiteligible = [lamBda * h for h in hiteligible]
                stickeligible = [lamBda * s for s in stickeligible]

                action = greedy(features, actionvalue, e)

        if lamBda in (0.0, 1.0):
            mses += [(game, mse(MCactionvalue, actionvalue))]
            plot(mses, 'Game', 'Mean square error', 'Lambda ' + str(lamBda))

        meansquarerror.append((lamBda, mse(MCactionvalue, actionvalue)))
    plot(meansquarerror, 'Lambda', 'Mean square error', 'MSE: Lambda 0.0-1.0')