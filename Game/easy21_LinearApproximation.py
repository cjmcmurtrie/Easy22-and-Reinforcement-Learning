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
actionglobal = [0, 1]


def mse(MCactionvalue, actionvalue):
    player = range(1,22)
    dealer = range(1,11)
    action = range(2)
    errors = []
    for p, d, a in product(player, dealer, action):
        state = State(p, d)
        features = linear(state, a)
        errors += [(actionvalue[tuple(features)] - MCactionvalue[(p, d, a)])**2]
    return sum(errors)/len(errors)


def linear(state, action):
    features = []
    for a, p, d in product(actionglobal, playercuboid, dealercuboid):
        if state.player in p and state.dealer in d and a==action: features += [1]
        else: features += [0]
    return features


def update(actionvalue, features, w):
    actionvalue[tuple(features)] = sum([x[0]*x[1] for x in zip(features, w)])
    return actionvalue


def greedysoft(state, actionvalue, w, e, actiononly):
    fhit = linear(state, 1); fstick = linear(state, 0)
    hit = actionvalue[tuple(fhit)]; stick = actionvalue[tuple(fstick)]
    if actiononly==1:
        if random() > e and hit != stick:
            if hit > stick: return 1
            else: return 0
        else: return randint(0, 1)
    else:
        if random() > e and hit != stick:
            if hit > stick: return 1, update(actionvalue, fhit, w), linear(state, 1)
            else: return 0, update(actionvalue, fstick, w), linear(state, 0)
        else:
            if random() > 0.5: action = 1
            else: action = 1
            features = linear(state, action); actionvalue = update(actionvalue, features, w)
            return action, actionvalue, features


if __name__ == '__main__':

    iterations = 1000
    lambdas = frange(0.0,1.1,0.1)
    meansquarerror = []
    MCactionvalue = pickle.load(open('MonteCarloActionValueFinal.p', 'rb'))

    for lamBda in lambdas:

        print "Lambda ", lamBda
        actionvalue = defaultdict(float)
        w = [0.0]*(3*6*2)
        e = 0.05
        a = 0.01
        mses = []

        for game in range(iterations):

            if lamBda in (0.0, 1.0): mses += [(game, mse(MCactionvalue, actionvalue))]

            Z = [0.0]*(3*6*2)
            state = State()
            action = greedysoft(state, actionvalue, w, e, 1)
            features = linear(state, action)

            while state.gameover==0:

                # Z = features; traces = 'Replaced traces'
                Z = [sum(x) for x in zip([lamBda * z for z in Z], features)]; traces = 'Accumulated traces'

                state, reward = step(state, action)
                d = reward - sum([x[0]*x[1] for x in zip(features, w)])

                if state.gameover==1:
                    w = [sum(x) for x in zip(w, [a * d * z for z in Z])]
                    break

                action, actionvalue, features = greedysoft(state, actionvalue, w, e, 0)
                d += actionvalue[tuple(features)]
                w = [sum(x) for x in zip(w, [a * d * z for z in Z])]

        if lamBda in (0.0, 1.0):
            mses += [(game, mse(MCactionvalue, actionvalue))]
            plot(mses, 'Game', 'Mean square error', 'Lambda = ' + str(lamBda) + ' . ' + traces)

        meansquarerror.append((lamBda, mse(MCactionvalue, actionvalue)))
    plot(meansquarerror, 'Lambda', 'Mean square error', 'MSE: Lambda 0.0-1.0')