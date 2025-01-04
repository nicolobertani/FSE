# Author: Mathieu Leng
# Date: 2023
# version 1.0

import os
import sys

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

class Model:
    """
    The Model class is responsible for the model part of the project.

    Attributes:
        - file_name: name of the file
        - iteration: number of iterations occured. One iteration is one choice.
        - sim_answers: dataframe containing calculated results such as p_x, z, w_p, s, and s_tilde
        - epsilon: biggest gap between the upper- and lowerbound
        - A1: matrix
        - lower_bound: value of the lower bound
        - upper_bound: value of the upper bound
        - D: gap between lower and upper bound
        - bound_list: list of bounds
    """
    
    ##### CONSTANTS
    order = 3
    helper = np.arange(0.01, 1, 0.01)
    chosen_xi = [.1, .9]
    m = 5
    
    def __init__(self, starting_p_x = .9, starting_z = (shared_info["x"] + shared_info["y"]) / 2):
        """
        Initiates the attributes
        """
        # questioning ---------------------------------------------------------------
        self.file_name = None
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
        self.A1 = np.zeros((self.m, self.m))
        np.fill_diagonal(self.A1, -1)

        self.lower_bound = I_spline(x=self.helper, k=self.order, interior_knots=self.chosen_xi, individual=True)[self.m-1]
        self.upper_bound = I_spline(x=self.helper, k=self.order, interior_knots=self.chosen_xi, individual=True)[0]
        self.D = self.upper_bound - self.lower_bound
        # create storage for bounds
        self.bound_list = [np.vstack((self.lower_bound, self.upper_bound))]

    def getEpsilon(self):
        return self.epsilon

    def getBoundlist(self):
        return self.bound_list

    def getSimAnswers(self):
        return self.sim_answers

    def setDirectoryFileName(self, directory, fileName):
        """
        Sets the directory and file name
        :param directory: directory in which to save the results in
        :param fileName: name of the file
        """
        self.directory = directory
        self.file_name = str(fileName) + ".csv"

    def saveSimAnswers(self):
        """
        Saves the results in sim_answers to a .csv file
        :return:
        """
        self.fileNameToSave = os.path.join(self.directory,self.file_name)
        self.sim_answers.dropna(subset=['s']).to_csv(self.fileNameToSave, index=False)

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

        # prepare parameters for LPs
        A2 = self.sim_answers["s_tilde"].values * I_spline(x = self.sim_answers["p_x"], k=self.order, interior_knots=self.chosen_xi, individual=True) # question part
        A = np.column_stack((self.A1, A2)).T
        b = np.concatenate((np.zeros(self.m), self.sim_answers["s_tilde"].values * self.sim_answers["w_p"].values))

        # update bounds
        for i, local_x in enumerate(self.helper):

            c = np.array(
                I_spline(x = local_x, k = 3, interior_knots = self.chosen_xi, individual = True)
            )

            min_problem = opt.linprog(
                c = c,
                A_ub = A,
                b_ub = b,
                A_eq = np.array([np.array([1] * self.m)]),
                b_eq = np.array([1])
            )
            self.lower_bound[i] = np.dot(min_problem.x, c)

            max_problem = opt.linprog(
                c = -c, # for maximization
                A_ub = A,
                b_ub = b,
                A_eq = np.array([np.array([1] * self.m)]),
                b_eq = np.array([1])
            )
            self.upper_bound[i] = np.dot(max_problem.x, c)

        # calculate max difference based on updated bounds
        self.D = np.round(self.upper_bound - self.lower_bound, 6)
        self.epsilon = np.max(self.D)

        # store bounds
        self.bound_list.append(np.vstack((self.lower_bound, self.upper_bound)))
        print(self.D)

        # update iteration
        self.iteration += 1
        self.sim_answers.loc[self.iteration, "q_n"] = self.iteration + 1

        # find next p
        candidates = self.D == np.max(self.D)
        if np.sum(candidates) == 1:  # if one point exists
            self.sim_answers.loc[self.iteration, "p_x"] = self.helper[candidates]
        else:  # if multiple points exist
            warnings.warn('Warning: multiple optimal bisection points')
            abs_distance_from_middle = np.abs(self.helper[candidates] - 0.5)
            self.sim_answers.loc[self.iteration, "p_x"] = np.array(self.helper[candidates])[abs_distance_from_middle == np.max(abs_distance_from_middle)][0]

        # compute next z and w.p
        w_p_t = (self.upper_bound + self.lower_bound)[self.helper == self.sim_answers.loc[self.iteration, "p_x"]] / 2 # p_w wiing lottery
        self.sim_answers.loc[self.iteration, "z"] = w_p_t * (shared_info["x"] - shared_info["y"]) + shared_info["y"] # z is sure amount
        self.sim_answers.loc[self.iteration, "w_p"] = w_p_t

        # saves z and p_w
        self.z = self.sim_answers.loc[self.iteration, "z"]
        self.p_x = self.sim_answers.loc[self.iteration, "p_x"]

        return self.z, self.p_x


model = Model()
model.calculate(0)
model.calculate(0)
model.calculate(0)
model.calculate(0)
model.calculate(0)
print(model.getSimAnswers())