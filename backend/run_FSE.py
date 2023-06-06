import numpy as np
from I_spline_M_spline import I_spline
import warnings
from scipy.optimize import linprog, minimize

order = 3
helper = np.arange(0.01, 1.0, 0.01)
chosen_xi = (.1, .9)
x = 120
y = 10

def run_FSE(epsilon_threshold=0.1):
    # questioning ---------------------------------------------------------------

    # initialization for questions
    sim_answers = np.empty((1, 5))
    sim_answers[:] = np.nan
    colnames = ['p.x', 'z', 'w.p', 's', 's.tilde']
    m = 5
    epsilon = np.inf
    iteration = 0
    # initialization for LPs
    A1 = np.zeros((m, m))
    np.fill_diagonal(A1, 1)
    # bounds with no answers
    lower_bound = I_spline(x=helper, k=order, interior_knots=chosen_xi, individual=True)[:, m]
    upper_bound = I_spline(x=helper, k=order, interior_knots=chosen_xi, individual=True)[:, 1]
    D = upper_bound - lower_bound
    # create storage for bounds
    bound_list = [np.vstack((lower_bound, upper_bound))]

    while epsilon > epsilon_threshold:
        iteration += 1

        # find next p
        candidates = D == np.max(D)
        if np.sum(candidates) == 1:  # if one point exists
            sim_answers[iteration, 0] = helper[candidates]
        else:  # if multiple points exist
            warnings.warn('Warning: multiple optimal bisection points')
            abs_distance_from_middle = np.abs(helper[candidates] - 0.5)
            sim_answers[iteration, 0] = np.tail(helper[candidates][abs_distance_from_middle == np.max(abs_distance_from_middle)], 1)

        # compute next z and w.p
        w_p_t = (upper_bound + lower_bound)[helper == sim_answers[iteration, 0]] / 2
        sim_answers[iteration, 1] = w_p_t * (x - y) + y
        sim_answers[iteration, 2] = w_p_t

        # asks the question and records the truth
        sim_answers[iteration, 3] = 1 #defining_function(sim_answers[iteration, 0]) < sim_answers[iteration, 2]
        sim_answers[iteration, 4] = 1 if sim_answers[iteration, 3] else -1

        # prepare parameters for LPs
        if iteration == 1:
            A2 = np.transpose(sim_answers[:, 4].reshape(-1, 1) * np.transpose(I_spline(x=sim_answers[:, 0], k=order, interior_knots=chosen_xi, individual=True)))
        else:
            A2 = np.transpose(sim_answers[:, 4].reshape(-1, 1) * I_spline(x=sim_answers[:, 0], k=order, interior_knots=chosen_xi, individual=True))
        b = np.concatenate(([1], np.zeros(m), sim_answers[:, 4] * sim_answers[:, 2]))
        constraint_signs = np.concatenate((["=="], np.repeat(">=", m), np.repeat("<=", sim_answers.shape[0])))
        A = np.transpose(np.vstack((np.repeat(1, m), A1, A2)))

        # calculate lower bound
        lower_bound = np.apply_along_axis(lambda local_x: minimize(lambda c: np.dot(c, I_spline(x=local_x, k=3, interior_knots=chosen_xi, individual=True)),
                                                                   np.zeros(m), bounds=[(None, None)] * m,
                                                                   constraints={'type': constraint_signs, 'fun': lambda c: np.dot(c, A.T) - b}).fun,
                                          axis=0, arr=helper)

        # calculate upper bound
        upper_bound = np.apply_along_axis(lambda local_x: minimize(lambda c: -np.dot(c, I_spline(x=local_x, k=order, interior_knots=chosen_xi, individual=True)),
                                                                   np.zeros(m), bounds=[(None, None)] * m,
                                                                   constraints={'type': constraint_signs, 'fun': lambda c: np.dot(c, A.T) - b}).fun,
                                          axis=0, arr=helper)

        # calculate max difference based on updated bounds
        D = upper_bound - lower_bound
        epsilon = np.max(D)

        # store bounds
        bound_list.append(np.vstack((lower_bound, upper_bound)))

    # representative shape ----------------------------------------------------

    sim_answers[:, 3] = sim_answers[:, 4]
    sim_answers[:, 4] = sim_answers[:, 4]
    sim_answers[:, 5] = sim_answers[:, 4] == sim_answers[:, 5]
    X = sim_answers[:, 2] - I_spline(x=sim_answers[:, 0], k=order, interior_knots=chosen_xi, individual=True)
    X = X * sim_answers[:, 3]
    # setup of constraints
    D = np.zeros((X.shape[1], X.shape[1]))
    np.fill_diagonal(D, 1)
    positive_constraint_matrix = 1 * D
    d = np.zeros(np.unique(D.shape))
    A = np.hstack((positive_constraint_matrix, np.transpose(X)))
    b = np.concatenate((np.repeat(0, positive_constraint_matrix.shape[1]), np.repeat(1, X.shape[0])))
    # solution
    res = linprog(c=d, A_ub=A, b_ub=b, method='simplex')
    normalized_solution = res.x / np.sum(res.x)
    lambda_constraints = res.slack[0:m] > 0
    support_vectors = res.slack[(m+1):] > 0

    # output ------------------------------------------------------------------

    return [sim_answers, np.vstack(bound_list), {"normalized_solution": normalized_solution,
                                                 "lambda_constraints": lambda_constraints,
                                                 "support_vectors": support_vectors},
            bound_list]
