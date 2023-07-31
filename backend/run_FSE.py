import numpy as np
import pandas as pd
from I_spline_M_spline import I_spline
import warnings
from scipy.optimize import linprog, minimize
import scipy.optimize as opt



order = 3
helper = np.arange(0.01, 1, 0.01)
chosen_xi = [.1, .9]
x = 120
y = 10
m = 5

def run_FSE(epsilon_threshold=0.1, verbose = False):
    # questioning ---------------------------------------------------------------

    # initialization for questions
    colnames = ['p_x', 'z', 'w_p', 's', 's_tilde']
    sim_answers = pd.DataFrame(columns=colnames)
    epsilon = np.inf
    iteration = 0
    # initialization for LPs
    A1 = np.zeros((m, m))
    np.fill_diagonal(A1, -1)
    if verbose:
        print("A1", A1)

    lower_bound = I_spline(x=helper, k=order, interior_knots=chosen_xi, individual=True)[m-1]
    upper_bound = I_spline(x=helper, k=order, interior_knots=chosen_xi, individual=True)[0]
    D = upper_bound - lower_bound
    # create storage for bounds
    bound_list = [np.vstack((lower_bound, upper_bound))]

    # while epsilon > epsilon_threshold:
    while iteration < 1:

        # find next p
        candidates = D == np.max(D)
        if np.sum(candidates) == 1:  # if one point exists
            sim_answers.loc[iteration, "p_x"] = helper[candidates]
        else:  # if multiple points exist
            warnings.warn('Warning: multiple optimal bisection points')
            abs_distance_from_middle = np.abs(helper[candidates] - 0.5)
            print("error", np.array(helper[candidates])[abs_distance_from_middle == np.max(abs_distance_from_middle)][-1])
            print('second error', sim_answers.loc[iteration, "p_x"])
            print("iteration", iteration)
            sim_answers.loc[iteration, "p_x"] = np.array(helper[candidates])[abs_distance_from_middle == np.max(abs_distance_from_middle)][-1]


        # compute next z and w.p
        w_p_t = (upper_bound + lower_bound)[helper == sim_answers.loc[iteration, "p_x"]] / 2
        sim_answers.loc[iteration, "z"] = w_p_t * (x - y) + y
        sim_answers.loc[iteration, "w_p"] = w_p_t

        # asks the question and records the truth
        sim_answers.loc[iteration, "s"] = 0 # @TODO check that correct because hard coded #defining_function(sim_answers[iteration, 0]) < sim_answers[iteration, 2]
        sim_answers.loc[iteration, "s_tilde"] = 1 if sim_answers.loc[iteration, "s"] else -1
        
        if verbose:
            print("sim answers", sim_answers)


        # prepare parameters for LPs
        if iteration == 1:
            A2 = np.transpose(sim_answers[:, 4].reshape(-1, 1) * np.transpose(I_spline(x=sim_answers[:, 0], k=order, interior_knots=chosen_xi, individual=True)))
        else:
            A2 = np.transpose(sim_answers[:, 4].reshape(-1, 1) * I_spline(x=sim_answers[:, 0], k=order, interior_knots=chosen_xi, individual=True))
        print("A2", A2) # the signs are the opposite
        A = np.column_stack((A1, A2)).T
        print("A", A)
        print("A", A.ndim)
        b = np.concatenate((np.zeros(m), sim_answers[:, 4] * sim_answers[:, 2]))
        print("b", b)


        for i, local_x in enumerate(helper):
            
            c = np.array(
                I_spline(x = local_x, k = 3, interior_knots = chosen_xi, individual = True) # the results of c are a bit different, but very close @ TODO check thats the error
            )
            
            if verbose:
                print("c", c)

            min_problem = opt.linprog(
                c = c,
                A_ub = A,
                b_ub = b,
                A_eq = np.array([np.array([1] * m)]),
                b_eq = np.array([1])
            )
            lower_bound[i] = np.dot(min_problem.x, c)

            max_problem = opt.linprog(
                c = -c,
                A_ub = A,
                b_ub = b,
                A_eq = np.array([np.array([1] * m)]),
                b_eq = np.array([1])
            )
            upper_bound[i] = np.dot(max_problem.x, c)

        
        # Print or use the lower_bound array as needed
        print("lower_bound", lower_bound)
        print("upper_bound", upper_bound)

        # calculate max difference based on updated bounds
        D = upper_bound - lower_bound
        epsilon = np.max(D)

        # store bounds
        bound_list.append(np.vstack((lower_bound, upper_bound)))
        
        iteration += 1

    # # representative shape ----------------------------------------------------

    # sim_answers[:, 3] = sim_answers[:, 4]
    # sim_answers[:, 4] = sim_answers[:, 4]
    # sim_answers[:, 5] = sim_answers[:, 4] == sim_answers[:, 5]
    # X = sim_answers[:, 2] - I_spline(x=sim_answers[:, 0], k=order, interior_knots=chosen_xi, individual=True)
    # X = X * sim_answers[:, 3]
    # # setup of constraints
    # D = np.zeros((X.shape[1], X.shape[1]))
    # np.fill_diagonal(D, 1)
    # positive_constraint_matrix = 1 * D
    # d = np.zeros(np.unique(D.shape))
    # A = np.hstack((positive_constraint_matrix, np.transpose(X)))
    # b = np.concatenate((np.repeat(0, positive_constraint_matrix.shape[1]), np.repeat(1, X.shape[0])))
    # # solution
    # res = linprog(c=d, A_ub=A, b_ub=b, method='simplex')
    # normalized_solution = res.x / np.sum(res.x)
    # lambda_constraints = res.slack[0:m] > 0
    # support_vectors = res.slack[(m+1):] > 0

    # # output ------------------------------------------------------------------

    # return [sim_answers, np.vstack(bound_list), {"normalized_solution": normalized_solution,
    #                                              "lambda_constraints": lambda_constraints,
    #                                              "support_vectors": support_vectors},
    #         bound_list]
    return(bound_list)


run_FSE()