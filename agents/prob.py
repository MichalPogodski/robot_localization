# prob.py
# This is

import random
import numpy as np

from gridutil import *

best_turn = {('N', 'E'): 'turnright',
             ('N', 'S'): 'turnright',
             ('N', 'W'): 'turnleft',
             ('E', 'S'): 'turnright',
             ('E', 'W'): 'turnright',
             ('E', 'N'): 'turnleft',
             ('S', 'W'): 'turnright',
             ('S', 'N'): 'turnright',
             ('S', 'E'): 'turnleft',
             ('W', 'N'): 'turnright',
             ('W', 'E'): 'turnright',
             ('W', 'S'): 'turnleft'}


class LocAgent:

    def __init__(self, size, walls, eps_perc, eps_move):
        self.size = size
        self.walls = walls
        # list of valid locations
        self.locations = list({*locations(self.size)}.difference(self.walls))
        # dictionary from location to its index in the list
        self.loc_to_idx = {loc: idx for idx, loc in enumerate(self.locations)}
        self.eps_perc = eps_perc
        self.eps_move = eps_move

        # previous action
        self.prev_action = None
        self.dir = None
        self.prev_dir = None
        prob = 1.0 / len(self.locations)
        self.P = prob * np.ones([len(self.locations)], dtype=np.float)
        self.dir_prob = np.zeros((len(self.locations)), dtype=str)
    def __call__(self, percept):
        # update posterior
        # TODO PUT YOUR CODE HERE
        # prob = 1.0 / len(self.locations)    ZERUJE OBLICZENIA CO KROK
        # self.P = prob * np.ones([len(self.locations)], dtype=np.float)  ZERUJE OBLICZENIA CO KROK
        # sensor prob
        sensor_prob = np.zeros((len(self.locations), 4), dtype=float)
        for idx, loc in enumerate(self.locations):
            prob = [1.0, 1.0, 1.0, 1.0]
            dirs = ['N', 'E', 'S', 'W']
            for i, neig in enumerate(dirs):
                neig_loc = nextLoc(loc, neig)
                if (neig in percept) == ((not legalLoc(neig_loc, self.size)) or (neig_loc in self.walls)):
                    prob[i] *= 0.9
                else:
                    prob[i] *= 0.1

            for i, dir in enumerate(dirs):
                pr_idx = 10
                for i, pr in enumerate(dirs):
                    if self.prev_dir == pr:
                        pr_idx = i
                if self.prev_action == "turnleft":
                    if (i - 1) < 0 : i = 4
                    prob[i-1] *= 0.95
                    prob[i] *= 0.05
                elif self.prev_action == "turnright":
                    if (i + 1) > 3: i = -1
                    prob[i + 1] *= 0.95
                    prob[i] *= 0.05

            sensor_prob[idx] = prob


            # dirs prob
            dirs = ['N', 'E', 'S', 'W']
            for idx, loc in enumerate(sensor_prob):
                max_prob = max(loc)
                for i, dir in enumerate(dirs):
                    if loc[i] == max_prob:
                        self.dir_prob[idx] = dirs[i]


        # transition prob
        transitions = np.zeros((len(self.locations), len(self.locations), 4), dtype=float)
        if self.prev_action == "forward":
            for idx, loc in enumerate(self.locations):
                next_loc = nextLoc(loc, dir_prob[idx])
                if (next_loc not in self.walls) and (legalLoc(next_loc, self.size)):
                    next_idx = self.loc_to_idx[next_loc]
                    transitions[idx, next_idx] = 0.95
                    transitions[idx, idx] = 0.05
                else:
                    transitions[idx, idx] = 1.0
        else:
            for idx, loc in enumerate(self.locations):
                transitions[idx, idx] = 1.0

        print('###############', transitions.shape, self.P.shape)
        self.P = np.dot(transitions.transpose(), self.P)
        self.P = sensor_prob.transpose() * self.P
        self.P /= np.sum(self.P)

        # -----------------------

        action = 'forward'
        # TODO CHANGE THIS HEURISTICS TO SPEED UP CONVERGENCE
        # if there is a wall ahead then lets turn
        if 'fwd' in percept:
            # higher chance of turning left to avoid getting stuck in one location
            action = np.random.choice(['turnleft', 'turnright'], 1, p=[0.8, 0.2])
        else:
            # prefer moving forward to explore
            action = np.random.choice(['forward', 'turnleft', 'turnright'], 1, p=[0.8, 0.1, 0.1])

        self.prev_action = action

        return action

    def getPosterior(self):
        # directions in order 'N', 'E', 'S', 'W'
        P_arr = np.zeros([self.size, self.size, 4], dtype=np.float)

        # put probabilities in the array
        # TODO PUT YOUR CODE HERE
        for idx, loc in enumerate(self.locations):
            P_arr[loc[0], loc[1]] = self.P[idx]


        # -----------------------

        return P_arr

    def forward(self, cur_loc, cur_dir):
        if cur_dir == 'N':
            ret_loc = (cur_loc[0], cur_loc[1] + 1)
        elif cur_dir == 'E':
            ret_loc = (cur_loc[0] + 1, cur_loc[1])
        elif cur_dir == 'W':
            ret_loc = (cur_loc[0] - 1, cur_loc[1])
        elif cur_dir == 'S':
            ret_loc = (cur_loc[0], cur_loc[1] - 1)
        ret_loc = (min(max(ret_loc[0], 0), self.size - 1), min(max(ret_loc[1], 0), self.size - 1))
        return ret_loc, cur_dir

    def backward(self, cur_loc, cur_dir):
        if cur_dir == 'N':
            ret_loc = (cur_loc[0], cur_loc[1] - 1)
        elif cur_dir == 'E':
            ret_loc = (cur_loc[0] - 1, cur_loc[1])
        elif cur_dir == 'W':
            ret_loc = (cur_loc[0] + 1, cur_loc[1])
        elif cur_dir == 'S':
            ret_loc = (cur_loc[0], cur_loc[1] + 1)
        ret_loc = (min(max(ret_loc[0], 0), self.size - 1), min(max(ret_loc[1], 0), self.size - 1))
        return ret_loc, cur_dir

    @staticmethod
    def turnright(cur_loc, cur_dir):
        dir_to_idx = {'N': 0, 'E': 1, 'S': 2, 'W': 3}
        dirs = ['N', 'E', 'S', 'W']
        idx = (dir_to_idx[cur_dir] + 1) % 4
        return cur_loc, dirs[idx]

    @staticmethod
    def turnleft(cur_loc, cur_dir):
        dir_to_idx = {'N': 0, 'E': 1, 'S': 2, 'W': 3}
        dirs = ['N', 'E', 'S', 'W']
        idx = (dir_to_idx[cur_dir] + 4 - 1) % 4
        return cur_loc, dirs[idx]
