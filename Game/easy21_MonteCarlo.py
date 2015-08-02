__author__ = 'Conan'

import pickle
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure, show
from numpy import zeros, meshgrid
from State import State
from easy21 import step
from random import random, randint
from itertools import product
from collections import defaultdict
from mpl_toolkits.mplot3d import Axes3D as ax
from matplotlib import cm


def plot(function, xlabel, ylabel, title):
    plt.style.use('ggplot')
    plt.subplot(211)
    plt.plot(*zip(*function))
    plt.title(title); plt.ylabel(ylabel); plt.xlabel(xlabel)
    plt.show()


def plotvalue(actionvalue):
    value = defaultdict(int)
    # Pick highest valued action for each (state, action)
    for av in actionvalue:
        value[(av[0], av[1])] = max(actionvalue[(av[0], av[1], 0)], actionvalue[(av[0], av[1], 1)])
    player, dealer = sorted(set([v[0] for v in value])), sorted(set([v[1] for v in value]))
    p, d = meshgrid(player,dealer)
    v = zeros((len(dealer), len(player)))
    for pc, dc in product(player, dealer):
        v[dc-1][pc-1] = value[(pc, dc)]
    fig = figure()
    axes = ax(fig)
    axes.set_xlabel("dealer")
    axes.set_ylabel("player")
    axes.plot_surface(d, p, v, rstride=1, cstride=1, cmap=cm.Blues, edgecolors='w', linewidth=0.5)
    show()


# Mean square error against previous action value to measure convergence and optimise policy
def mse(checkactionvalue, currentactionvalue):
    player = range(1,22)
    dealer = range(1,11)
    action = [0, 1]
    errors = []
    for p, d, a in product(player, dealer, action):
        errors += [(currentactionvalue[(p, d, a)] - checkactionvalue[(p, d, a)])**2]
    return sum(errors)/len(errors)


# Calculate epsilon for constant Nzero
def epsilon(Nzero, Nstate, state):
    return Nzero / (Nzero + Nstate[(state.player,state.dealer)])


# Initialise functions as defaultdicts
def initialisefunctions():
    return defaultdict(float), defaultdict(float), defaultdict(float)


def greedysoft(state, actionvalue, e):
    hit = actionvalue[(state.player, state.dealer, 1)]
    stick = actionvalue[(state.player, state.dealer, 0)]
    if random() > e and hit != stick:
        if hit > stick: return 1
        return 0
    else:
        return randint(0, 1)


if __name__ == '__main__':

    Nzero = 10000.0
    game = 1.0
    converged = 10.0**-12
    errors = []; meanerror = [(0, 0.0), (0, 100.0)]

    # action value function as dictionary: (player, dealer, action) -> value
    actionvalue, Ns, Nsa = initialisefunctions()

    # Continue looping until MSE change is below threshold
    while meanerror[-1][1] > converged:

        game += 1.0
        state = State()
        episode = []

        # Generate episode
        while state.gameover==0:
            e = epsilon(Nzero, Ns, state)
            action = greedysoft(state, actionvalue, e)
            episode.append((state.player, state.dealer, action))
            state, reward = step(state, action)

        # Update functions
        episode = set(episode)
        for sa in episode:
            Ns[(sa[0],sa[1])] += 1.0
            Nsa[sa] += 1.0
            actionvalue[sa] += Nsa[sa]**-1 * (reward - actionvalue[sa])


        # ----- Outside algorithm - convergence and epsilon checks ------------
        # Save action-value at 5000th episode to compare action value at 10000th episode
        if game % 10000==5000:
            lastactionvalue = actionvalue.copy()

        if game % 100000==0:
            eps = [epsilon(Nzero, Ns, State(p, d)) for p, d in product(range(1, 22), range(1, 11))]
            print "Maximum epsilon: ", max(eps), " minimum epsilon: ", min(eps)
            print

        # Convergence calculations, moving average of previous 20 MSE
        if game % 10000==0:
            errors.append(mse(lastactionvalue, actionvalue))
            if game > 190000:
                meanerror.append((game, sum(errors[-20:])/len(errors[-20:])))
                print "Game: ", game, ". Moving average, MSE compared to 5,000 episodes previous: ", meanerror[-1][1]

    # # save results
    # pickle.dump(value, open("MonteCarloValueFinal.p", "wb" ))
    # pickle.dump(actionvalue, open("MonteCarloActionValueFinal.p", "wb" ))

    # Plots
    plotvalue(actionvalue)
    # plot(zip(range(210), eps), 'State', 'Epsilon', 'Distribution of epsilon(state) value')
    plot(meanerror[20:], 'Episode', 'MSE moving average', 'Convergence for Nzero = ' + str(Nzero))
