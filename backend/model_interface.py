import numpy as np
import pandas as pd
from backend.I_spline_M_spline import I_spline
import warnings
import scipy.optimize as opt
import csv



order = 3
helper = np.arange(0.01, 1, 0.01)
chosen_xi = [.1, .9]
x = 120
y = 10
m = 5

class Model:
    def __init__(self):
        # questioning ---------------------------------------------------------------
        self.verbose = False
        self.iteration = 0

        # initialization for questions
        colnames = ['p_x', 'z', 'w_p', 's', 's_tilde']
        self.sim_answers = pd.DataFrame(columns=colnames) # better to work with several iteration
        if self.verbose:
            print("sim_answers", self.sim_answers)

        self.epsilon = np.inf
        # initialization for LPs
        self.A1 = np.zeros((m, m))
        np.fill_diagonal(self.A1, -1)
        if self.verbose:
            print("A1", self.A1)

        self.lower_bound = I_spline(x=helper, k=order, interior_knots=chosen_xi, individual=True)[m-1]
        self.upper_bound = I_spline(x=helper, k=order, interior_knots=chosen_xi, individual=True)[0]
        self.D = self.upper_bound - self.lower_bound
        # create storage for bounds
        self.bound_list = [np.vstack((self.lower_bound, self.upper_bound))]
        self.z = -1 # sentinel value
        self.p_w = -1 # sentinel value

    def get_epsilon(self):
        return self.epsilon

    def get_boundlist(self):
        return self.bound_list

    def get_sim_answers(self):
        return self.sim_answers

    def save_sim_answers(self):
        with open('studentsq.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(self.sim_answers)


    def calculate(self, answer):

        # find next p
        candidates = self.D == np.max(self.D)
        if np.sum(candidates) == 1:  # if one point exists
            self.sim_answers.loc[self.iteration, "p_x"] = helper[candidates]
        else:  # if multiple points exist
            warnings.warn('Warning: multiple optimal bisection points')
            abs_distance_from_middle = np.abs(helper[candidates] - 0.5)
            self.sim_answers.loc[self.iteration, "p_x"] = np.array(helper[candidates])[abs_distance_from_middle == np.max(abs_distance_from_middle)][-1]

        # compute next z and w.p
        w_p_t = (self.upper_bound + self.lower_bound)[helper == self.sim_answers.loc[self.iteration, "p_x"]] / 2 # p_w wiing lottery
        self.sim_answers.loc[self.iteration, "z"] = w_p_t * (x - y) + y # z is sure amount
        self.sim_answers.loc[self.iteration, "w_p"] = w_p_t

        # saves z and p_w
        self.z = self.sim_answers.loc[self.iteration, "z"]
        self.p_w = self.sim_answers.loc[self.iteration, "w_p"]

        # asks the question and records the truth
        self.sim_answers.loc[self.iteration, "s"] = answer
        self.sim_answers.loc[self.iteration, "s_tilde"] = 1 if self.sim_answers.loc[self.iteration, "s"] else -1

        if self.verbose:
            print("sim answers\n", self.sim_answers)
            print(self.sim_answers["p_x"])
            print(self.sim_answers["s_tilde"])


        # prepare parameters for LPs
        A2 = self.sim_answers["s_tilde"].values * I_spline(x = self.sim_answers["p_x"], k=order, interior_knots=chosen_xi, individual=True) # question part
        A = np.column_stack((self.A1, A2)).T
        b = np.concatenate((np.zeros(m), self.sim_answers["s_tilde"].values * self.sim_answers["w_p"].values))
        if self.verbose:
            print("A2", A2) # the signs are the opposite
            print("A", A)
            print("A", A.ndim)
            print("b", b)


        for i, local_x in enumerate(helper):

            c = np.array(
                I_spline(x = local_x, k = 3, interior_knots = chosen_xi, individual = True)
            )

            if self.verbose:
                print("c", c)

            min_problem = opt.linprog(
                c = c,
                A_ub = A,
                b_ub = b,
                A_eq = np.array([np.array([1] * m)]),
                b_eq = np.array([1])
            )
            self.lower_bound[i] = np.dot(min_problem.x, c)

            max_problem = opt.linprog(
                c = -c, # for maximization
                A_ub = A,
                b_ub = b,
                A_eq = np.array([np.array([1] * m)]),
                b_eq = np.array([1])
            )
            self.upper_bound[i] = np.dot(max_problem.x, c)


        # Print or use the lower_bound array as needed
        if self.verbose:
            print("lower_bound", self.lower_bound)
            print("upper_bound", self.upper_bound)

        # calculate max difference based on updated bounds
        self.D = self.upper_bound - self.lower_bound
        self.epsilon = np.max(self.D)

        # store bounds
        self.bound_list.append(np.vstack((self.lower_bound, self.upper_bound)))

        self.iteration += 1

        return self.z, self.p_w





# @TODO
# save as .csv with no overwrite and save after every answer
# sim_answers

# ask the user for a number and this  number is saved for the file
# or choose unique identifier

# ideally query for location but can be turned off and create results folder i the smae location.


# write the instructions on how to use the code --> README
