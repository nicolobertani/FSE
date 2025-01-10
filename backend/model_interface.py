# Author: Mathieu Leng
# Date: 2023
# version 1.0

import os
import sys
import datetime

# define the path to the folder
file_path = os.path.abspath(__file__)
folder_path = os.path.dirname(file_path)
sys.path.insert(0, folder_path) 


import warnings
import numpy as np
import pandas as pd
import scipy.optimize as opt
from I_spline_M_spline import I_spline
from shared_info import shared_info

class FSE:
    """
    The FSE class is responsible for integrating FSE into main.
    """
    
    ##### CONSTANTS
    ORDER = 3
    CHOSEN_XI = [.1, .9]
    M = 5
    
    def __init__(self, 
                 starting_p_x = .9, 
                 starting_z = (shared_info["x"] + shared_info["y"]) / 2,
                 set_p = shared_info["set_p"],
                 set_z = None
                 ):
        """
        Initiates the attributes
        """
        # questioning ---------------------------------------------------------------
        self.set_p = set_p
        self.set_z = set_z
        self.iteration = 0

        # initialization for question dataframe
        starting_data = [[self.iteration + 1], [starting_p_x], [starting_z], [(starting_z - shared_info["y"]) / (shared_info["x"] - shared_info["y"])], [None], [None]]
        colnames = ['q_n', 'p_x', 'z', 'w_p', 's', 's_tilde']
        self.sim_answers = pd.DataFrame(
            dict(zip(colnames, starting_data))
            ) 
        
        # first question
        self.z = self.sim_answers.loc[self.iteration, "z"]
        self.p_w = self.sim_answers.loc[self.iteration, "p_x"]

        # initialization for LPs
        self.epsilon = np.inf
        self.A1 = np.zeros((FSE.M, FSE.M))
        np.fill_diagonal(self.A1, -1)

        self.lower_bound = I_spline(x=self.set_p, k=FSE.ORDER, interior_knots=self.CHOSEN_XI, individual=True)[FSE.M-1]
        self.upper_bound = I_spline(x=self.set_p, k=FSE.ORDER, interior_knots=self.CHOSEN_XI, individual=True)[0]
        self.D = self.upper_bound - self.lower_bound
        # create storage for bounds
        self.bound_list = [np.vstack((self.lower_bound, self.upper_bound))]

    def get_closest_z(self, z):
        """
        Returns the closest bisection point in the set z
        """
        distances = np.abs(np.array(self.set_z) - z)
        closest_indices = np.where(distances == np.min(distances))[0]
        closest_z_values = np.array(self.set_z)[closest_indices]
        
        if len(closest_z_values) > 1:
            closest_z = np.random.choice(closest_z_values)
        else:
            closest_z = closest_z_values[0]
        
        return closest_z

    def getEpsilon(self):
        return self.epsilon

    def getBoundlist(self):
        return self.bound_list

    def getSimAnswers(self):
        return self.sim_answers

    def calculate(self, answer):
        """
        Calculates the next values for the lottery after the user's answer
        :param
            - answer: the user's answer
        :return:
            - self.z: sure value
            - self.p_w: weighted probability
        """

        # asks the question and records the truth
        self.sim_answers.loc[self.iteration, "s"] = int(answer)
        self.sim_answers.loc[self.iteration, "s_tilde"] = 1 if self.sim_answers.loc[self.iteration, "s"] else -1

        # record the current time
        self.sim_answers.loc[self.iteration, "timestamp"] = datetime.datetime.now()

        # prepare parameters for LPs
        A2 = self.sim_answers["s_tilde"].values * I_spline(x = self.sim_answers["p_x"], k=FSE.ORDER, interior_knots=self.CHOSEN_XI, individual=True) # question part
        A = np.column_stack((self.A1, A2)).T
        b = np.concatenate((np.zeros(FSE.M), self.sim_answers["s_tilde"].values * self.sim_answers["w_p"].values))

        # update bounds
        for i, local_x in enumerate(self.set_p):

            c = np.array(
                I_spline(x = local_x, k = 3, interior_knots = self.CHOSEN_XI, individual = True)
            )

            min_problem = opt.linprog(
                c = c,
                A_ub = A,
                b_ub = b,
                A_eq = np.array([np.array([1] * FSE.M)]),
                b_eq = np.array([1])
            )
            self.lower_bound[i] = np.dot(min_problem.x, c)

            max_problem = opt.linprog(
                c = -c, # for maximization
                A_ub = A,
                b_ub = b,
                A_eq = np.array([np.array([1] * FSE.M)]),
                b_eq = np.array([1])
            )
            self.upper_bound[i] = np.dot(max_problem.x, c)

        # calculate max difference based on updated bounds
        self.D = np.round(self.upper_bound - self.lower_bound, 6)
        self.epsilon = np.round(np.max(self.D), 4)

        # store bounds
        self.bound_list.append(np.vstack((self.lower_bound, self.upper_bound)))

        # update iteration
        self.iteration += 1
        self.sim_answers.loc[self.iteration, "q_n"] = self.iteration + 1

        # find next p
        candidates = self.D == np.max(self.D)
        if np.sum(candidates) == 1:  # if one point exists
            self.sim_answers.loc[self.iteration, "p_x"] = self.set_p[candidates]
        else:  # if multiple points exist
            warnings.warn('Warning: multiple optimal bisection points')
            abs_distance_from_middle = np.abs(self.set_p[candidates] - 0.5)
            self.sim_answers.loc[self.iteration, "p_x"] = np.array(self.set_p[candidates])[abs_distance_from_middle == np.max(abs_distance_from_middle)][0]

        # compute next z and w.p
        w_p_t = (self.upper_bound + self.lower_bound)[self.set_p == self.sim_answers.loc[self.iteration, "p_x"]] / 2 # p_w wiing lottery
        candidate_z_t = w_p_t * (shared_info["x"] - shared_info["y"]) + shared_info["y"] # z is sure amount
        if (self.set_z is None):
            self.sim_answers.loc[self.iteration, "z"] = candidate_z_t
            self.sim_answers.loc[self.iteration, "w_p"] = w_p_t
        else:
            self.sim_answers.loc[self.iteration, "z"] = self.get_closest_z(candidate_z_t)
            self.sim_answers.loc[self.iteration, "w_p"] = (self.sim_answers.loc[self.iteration, "z"] - shared_info["y"]) / (shared_info["x"] - shared_info["y"])

        # saves z and p_w
        self.z = self.sim_answers.loc[self.iteration, "z"]
        self.p_x = self.sim_answers.loc[self.iteration, "p_x"]

        return self.z, self.p_x
