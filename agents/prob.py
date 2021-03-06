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
        self.prev_action = 'forward'

        prob = 1.0 / len(self.locations) / 4.0
        self.P = prob * np.ones([len(self.locations), 4], dtype=np.float)



    def __call__(self, percept):
        # update posterior
        # TODO PUT YOUR CODE HERE
        dirs = ['N', 'E', 'S', 'W']

        # sensor prob
        sensor_prob = np.ones((len(self.locations), 4), dtype=float)
        for idx, loc in enumerate(self.locations):
            for i, neig in enumerate(dirs):
                translated = []
                pom_dict = {}
                # creating a dict. contained translated sensor information (sens. info to directory)
                if neig == 'N':
                    pom_dict['fwd'] = 'N'
                    pom_dict['right'] = 'E'
                    pom_dict['bckwd'] = 'S'
                    pom_dict['left'] = 'W'
                elif neig == 'E':
                    pom_dict['fwd'] = 'E'
                    pom_dict['right'] = 'S'
                    pom_dict['bckwd'] = 'W'
                    pom_dict['left'] = 'N'
                elif neig == 'S':
                    pom_dict['fwd'] = 'S'
                    pom_dict['right'] = 'W'
                    pom_dict['bckwd'] = 'N'
                    pom_dict['left'] = 'E'
                elif neig == 'W':
                    pom_dict['fwd'] = 'W'
                    pom_dict['right'] = 'N'
                    pom_dict['bckwd'] = 'E'
                    pom_dict['left'] = 'S'

                for elem in percept:
                    if elem != 'bump':
                        translated.append(pom_dict[elem])

                for j, obst in enumerate(dirs):
                    if 'bump' in percept:
                        if (not legalLoc(nextLoc(loc, obst), self.size) or (nextLoc(loc, obst) in self.walls)):
                            # if robot hit the wall and next_loc in particular direction is a wall (or not in a map)
                            sensor_prob[idx, j] *= 1.0
                        else:
                            # if robot hit the wall and next_loc in particular direction is not a wall (and it's contained in the map)
                            sensor_prob[idx, j] *= 0.0
                    elif (obst in translated) == ((not legalLoc(nextLoc(loc, obst), self.size)) or (nextLoc(loc, obst) in self.walls)):
                        sensor_prob[idx, j] *= (1.0 - self.eps_perc)
                    else:
                        sensor_prob[idx, j] *= self.eps_perc

        sensor_prob = sensor_prob.flatten('F')


        # transition prob
        transitions = np.zeros((4 * len(self.locations), 4 * len(self.locations)), dtype=float)
        for idx, loc in enumerate(self.locations):
            for i, dir in enumerate(dirs):
                if self.prev_action == "forward":
                    # if robot hit the wall and next_loc in particular direction is a wall, robot stay in the same place
                    if 'bump' in percept == ((not legalLoc(nextLoc(loc, dir), self.size)) or (nextLoc(loc, dir) in self.walls)):
                        transitions[idx, idx] = 1.0
                    elif (nextLoc(loc, dir) not in self.walls) and (legalLoc(nextLoc(loc, dir), self.size)):
                        next_loc = nextLoc(loc, dir)
                        next_idx = self.loc_to_idx[next_loc]
                        # robot will change location with (1 - eps_move) possibility
                        transitions[idx + (i * len(self.locations)), next_idx + (i * len(self.locations))] = (1.0 - self.eps_move)
                        transitions[idx + (i * len(self.locations)), idx + (i * len(self.locations))] = self.eps_move
                    else:
                        transitions[idx + (i * len(self.locations)), idx + (i * len(self.locations))] = 1.0

                # robot will change direction with (1 - eps_move) possibility
                elif self.prev_action == "turnright":
                    transitions[idx + (i * len(self.locations)), (idx + (i * len(self.locations)) + len(self.locations)) % (4 * len(self.locations))] = (1.0 - self.eps_move)
                    transitions[idx + (i * len(self.locations)), idx + (i * len(self.locations))] = self.eps_move

                # robot will change direction with (1 - eps_move) possibility
                elif self.prev_action == "turnleft":
                    transitions[idx + (i * len(self.locations)), (idx + (i * len(self.locations)) - len(self.locations)) % (4 * len(self.locations))] = (1.0 - self.eps_move)
                    transitions[idx + (i * len(self.locations)), idx + (i * len(self.locations))] = self.eps_move



        temp_P = self.P.flatten('F')
        temp_P = np.multiply(sensor_prob, np.dot(transitions.transpose(), temp_P))
        self.P = np.reshape(temp_P, (len(self.locations), 4), 'F')
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
