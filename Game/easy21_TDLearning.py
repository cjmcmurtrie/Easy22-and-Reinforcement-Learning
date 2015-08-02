__author__ = 'Conan'


from easy21_MonteCarlo import epsilon, initialisefunctions, greedysoft, mse, plot
from easy21 import step
from State import State
from collections import defaultdict
from numpy import arange as frange
from copy import copy
import pickle


if __name__ == '__main__':

    lambdas = frange(0.0,1.1,0.1)
    meansquarerror = []
    iterations = 1000
    discount = 1.0
    MCactionvalue = pickle.load(open('MonteCarloActionValueFinal.p', 'rb'))

    for lamBda in lambdas:
        print "Lambda ", lamBda

        actionvalue, Ns, Nsa = initialisefunctions()
        Nsa = defaultdict(lambda: 1.0)
        Nzero = 100.0
        mses = []

        for game in range(iterations):
            if lamBda in (0.0, 1.0): mses += [(game, mse(MCactionvalue, actionvalue))]

            Z = defaultdict(float)
            state = State()
            e = epsilon(Nzero, Ns, state)
            action = greedysoft(state, actionvalue, e)
            episode = []

            while state.gameover==0:

                Nsa[(state.player, state.dealer, action)] += 1
                Ns[(state.player, state.dealer)] += 1
                episode += [(state.player, state.dealer, action)]
                startstate = copy(state)

                # Take action A, observe reward, S
                state, reward = step(state, action)
                e = epsilon(Nzero, Ns, state)

                # Choose A' from S' using Q policy
                ingameaction = greedysoft(state, actionvalue, e)

                # Delta = R + gamma*Q' + Q; Z = Z + 1
                d = reward + ( discount * actionvalue[(state.player, state.dealer, ingameaction)] ) - actionvalue[(startstate.player, startstate.dealer, action)]
                Z[(startstate.player, startstate.dealer, action)] += 1
                stateaction = (state.player, state.dealer, action)

                for stateaction in episode:
                    a = Nsa[stateaction] ** -1
                    actionvalue[stateaction] += a * d * Z[stateaction]
                    Z[stateaction] *= lamBda

                action = ingameaction

        if lamBda in (0.0, 1.0):
            mses += [(game, mse(MCactionvalue, actionvalue))]
            plot(mses, 'Episode', 'Mean square error', 'Lambda ' + str(lamBda))


        meansquarerror.append((lamBda, mse(actionvalue, MCactionvalue)))

    plot(meansquarerror, 'Lambda', 'Mean square error', 'MSE: Lambda 0.0-1.0')
