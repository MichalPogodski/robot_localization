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
        self.P = prob * np.ones([len(self.locations), 4], dtype=np.float)
        self.new_dir = ['N', 'N', 'N', 'N']
        self.new_dir_prob = [0.0, 0.0, 0.0, 0.0]


    def __call__(self, percept):
        # update posterior
        # TODO PUT YOUR CODE HERE

        # sensor prob
        sensor_prob = np.zeros((len(self.locations), 4), dtype=float)
        for idx, loc in enumerate(self.locations):
            prob = 1.0
            dirs = ['N', 'E', 'S', 'W']
            for i, neig in enumerate(dirs):
                neig_loc = nextLoc(loc, neig)
                translated = []
                pom_dict = {}
                pom_dict['fwd'] = 'N'
                pom_dict['right'] = 'E'
                pom_dict['bckwd'] = 'S'
                pom_dict['left'] = 'W'
                if self.dir == 'N':
                    pom_dict['fwd'] = 'N'
                    pom_dict['right'] = 'E'
                    pom_dict['bckwd'] = 'S'
                    pom_dict['left'] = 'W'
                elif self.dir == 'E':
                    pom_dict['fwd'] = 'E'
                    pom_dict['right'] = 'S'
                    pom_dict['bckwd'] = 'W'
                    pom_dict['left'] = 'N'
                elif self.dir == 'S':
                    pom_dict['fwd'] = 'S'
                    pom_dict['right'] = 'W'
                    pom_dict['bckwd'] = 'N'
                    pom_dict['left'] = 'E'
                elif self.dir == 'W':
                    pom_dict['fwd'] = 'W'
                    pom_dict['right'] = 'N'
                    pom_dict['bckwd'] = 'E'
                    pom_dict['left'] = 'S'

                if 'bump' not in percept:
                    for elem in percept: translated.append(pom_dict[elem])

                    if (neig in translated) == ((not legalLoc(neig_loc, self.size)) or (neig_loc in self.walls)):
                        prob *= 0.9
                    else:
                        prob *= 0.1
                else:
                    prob *= 1.0

            sensor_prob[idx] = [prob, prob, prob, prob]


        # transition prob
        transitions = np.zeros((len(self.locations), len(self.locations)), dtype=float)
        if self.prev_action == "forward":
            for idx, loc in enumerate(self.locations):
                next_loc = nextLoc(loc, self.dir)
                if (next_loc not in self.walls) and (legalLoc(next_loc, self.size)):
                    next_idx = self.loc_to_idx[next_loc]
                    transitions[idx, next_idx] = 0.95
                    transitions[idx, idx] = 0.05
                else:
                    transitions[idx, idx] = 1.0
        else:
            for idx, loc in enumerate(self.locations):
                transitions[idx, idx] = 1.0


        # direction prob
        self.prev_dir = self.dir
        dir_prob = np.ones([4, 4], dtype=np.float)
        for i in range(4):
            if self.prev_action == "turnleft":
                dir_prob[(i + 3) % 4, (i + 3) % 4] *= 0.95
                dir_prob[i, i] *= 0.05
            elif self.prev_action == "turnright":
                dir_prob[(i + 1) % 4, (i + 1) % 4] *= 0.95
                dir_prob[i, i] *= 0.05
        for i in range(4):
            for j in range(4):
                if dir_prob[i, j] == max(dir_prob[i]):
                    self.new_dir[i] = dirs[i]
                    self.new_dir_prob[i] = max(dir_prob[i])
        for i in range(4):
            if self.new_dir_prob[i] == max(self.new_dir_prob): self.dir = self.new_dir[i]


        self.P = np.dot(transitions.transpose(), self.P)
        self.P = sensor_prob * np.dot(self.P, dir_prob)
        self.P /= np.sum(self.P)

        # -----------------------


        action = 'forward'
        # TODO CHANGE THIS HEURISTICS TO SPEED UP CONVERGENCE

        if 'right' not in percept and self.prev_action != 'turnright':
            action = 'turnright'
        elif 'fwd' not in percept:
            action = 'forward'
        else:
            action = 'turnleft'

        self.prev_action = action

        return action


    def getPosterior(self):
        # directions in order 'N', 'E', 'S', 'W'
        P_arr = np.zeros([self.size, self.size, 4], dtype=np.float)

        # put probabilities in the array
        # TODO PUT YOUR CODE HERE
        pom = np.zeros(len(self.locations), dtype = float)
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
