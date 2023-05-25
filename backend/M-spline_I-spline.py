import warnings
import numpy as np
import statsmodel.api as sm
import matplotlib.pyplot as plt
from numpy.testing import suppress_warnings
import cvxpy as cp
import importlib
from scipy.stats import sem, percentileofscore

def M_knots_sequence(k, interior_knots, boundary_knots=(0, 1)):
    """
    Generates knots sequence for basis M spline
    :param k:
    :param interior_knots:
    :param boundary_knots:
    :return:
    """
    t = [min(boundary_knots)] * k + interior_knots + [max(boundary_knots)] * k
    return t

def M_basis(i, x, k, t): #@ TODO check that the vectorize is correct
    # be careful with indexes, ≠ than in R
    if ( i + k > len(t)):
        raise ValueError("i + k > |t|.")
    if x == 1:
        x -= 1 * 10 ** -8
        # @ TODO here the code is unclear
    out = 0
    if k == 1:
        if t[i] <= x < t[i + 1]:
            out = 1 / t[i+1] - t[i]
    else:
        if t[i+k] > t[i]:
            out = k * ((x - t[i]) * M_basis(i, x, k - 1, t) + (t[i + k] - x) * M_basis(i + 1, x, k - 1, t))  / ((k - 1) * (t[i + k] - t[i]))
    return out

def M_spline( k, interior_knots, individual = False, boundary_knots = (0,1),  lambdas = None, x=0):
    t = M_knots_sequence(k, interior_knots, boundary_knots)
    m = len(t)- k
    if len(lambdas) != m or len(lambdas) != m:
        raise ValueError("Incorrect number of lambdas. Need ", m, "lambdas.")

    if len(lambdas) and individual:
        warnings.warn("lambdas are compatible with individual output.")

    if not len(lambdas):
        lambdas = [1/m for _ in range(m)]

    if sum(lambdas) != 1:
        warnings.warn("Lambdas do no sum up to 1.")

    if individual:
        out = np.apply_along_axis(lambda i: M_basis(i, x, k, t), axis=0, arr=np.arange(1, m+1))
    else:
        out = np.apply_along_axis(lambda i: M_basis(i, x, k, t), axis=0, arr=np.arange(1, m+1)).dot(lambdas)
    return out

def plot_M_spline(y, k, interior_knots, x=None, boundary_knots = (0,1), point_type = 21, point_size = .8, point_color = (0.2, 0.2, 0.2, 0.8), *args):
    t = M_knots_sequence(k, interior_knots, boundary_knots)
    m = len(t) - k
    if not x: # @ TODO check equivalent
        y = sorted(y)
        x = np.linspace(0, 1, num = len(y))

    #model_formula = "y ~ " + " + ".join([f"M_basis({i}, x, k, t)" for i in range(1, m+1)]) + " + 0"
    model = sm.OLS(y, sm.add_constant([f"M_basis({i}, x, k, t)" for i in range(1, m+1)])).fit()
    plt.scatter(x, y, marker=point_type, s=point_size, c=point_color, edgecolors='none', alpha=0.5)

    x_sorted = np.sort(x)
    y_spline = suppress_warnings(M_spline(x_sorted, k, interior_knots, boundary_knots, model.coef_))
    plt.plot(x_sorted, y_spline, '-g', linewidth=2)

    v_lines = np.concatenate([interior_knots, boundary_knots])
    for v_line in v_lines:
        plt.axvline(x=v_line, linestyle='--', color='gray', linewidth=2)

    plt.show()
    return model

def I_knots_sequence(k, interior_knots, boundary_knots = (0,1)):
    t = [min(boundary_knots)] * (k+1) + interior_knots + [max(boundary_knots)] * (k+1)
    return t


def I_basis(i, x, k, t): #@ TODO check that the vectorize is correct
    # be careful with indexes, ≠ than in R
    if i not in [x for x in range(1, len(t)-k)]:
        raise ValueError("i > m = len(t) -k.")
    if x == 1:
        pass
        # @ TODO here the code is unclear
    j = np.dot(np.arange(len(t)).reshape(-1, 1), ((x >= t) & (x < np.concatenate((t[1:], [1])))).reshape(1, -1))

    if i > j:
        out = 0
    else:
        if i < j - k + 1:
            out = 1
        else:
            out = np.dot((t[i:j + k + 1] - t[i:j]) / (k + 1), np.apply_along_axis(lambda i: M_basis(i, x, k + 1, t), axis=0, arr=np.arange(i, j + 1)))

    return out

def I_spline(k, interior_knots, x=0, lambdas=None, individual=False, boundary_knots = (0,1), exclude_constant_splines = True):
    t = I_knots_sequence(k, interior_knots, boundary_knots)
    value = 2
    if not exclude_constant_splines:
        value = 0
    m = len(t) - k - value
    if not lambdas or lambdas not in (0,m):
        raise ValueError("Incorrect number of lambdas. Need ", m, " lambdas.")
    if not lambdas and len(lambdas) and individual:
        warnings.warn("lambdas are compatible with individual output.")
    if not len(lambdas):
        lambdas = [1/m for _ in range(m)]
    if sum(lambdas) < .9999 or sum(lambdas) > 1.0001:
        warnings.warn("Lambdas do not sum up to 1.")
    i_sequence = 2 if exclude_constant_splines else 1, m+1 if exclude_constant_splines else m
    i_sequence = [i for i in range(i_sequence[0], i_sequence[1])]

    if individual:
        out = [I_basis(i, x, k, t) for i in i_sequence]
    else:
        out = np.dot(np.array([I_basis(i, x, k, t) for i in i_sequence]), lambdas)
    return out

def fit_I_spline_L2(y, x, k, interior_knots, *args):
    X = I_spline(x = sorted(x), k = k, individual = True, interior_knots = interior_knots,*args)
    Dmat = np.dot(X.T, X)
    d = np.dot(X.T, y)
    Amat = np.vstack((np.ones((1, np.unique(Dmat.shape))), np.eye(np.unique(Dmat.shape))))
    b = np.hstack((1, np.zeros(np.unique(Dmat.shape))))
    x = cp.Variable(Dmat.shape[1])
    objective = cp.Minimize(0.5 * cp.quad_form(x, Dmat) - d @ x)
    constraints = [Amat @ x == b]
    problem = cp.Problem(objective, constraints)
    problem.solve()
    out = x.value
    return out

def fit_I_spline( k, interior_knots, y = None, x = None, boundary_knots = (0,1), exclude_constant_splines = True,
                 L2 = True, inference = False, bootstrap_n = 100, point_type = 21, point_size = .8, point_color = (0.2, 0.2, 0.2, 0.8), *args):
    """
    not used
    :param k:
    :param interior_knots:
    :param y:
    :param x:
    :param boundary_knots:
    :param exclude_constant_splines:
    :param L2:
    :param inference:
    :param bootstrap_n:
    :param point_type:
    :param point_size:
    :param point_color:
    :param args:
    :return:
    """
    if y and x and len(y) != len(x):
        raise ValueError("x and y need to be of the same length.")
    if not x:
        y = sorted(y)
        x = np.linspace(0, 1, len(y))
    if L2 and True:
        pass #@TODO not clear here

    if L2:
        model = fit_I_spline_L2(y, x, k, interior_knots, boundary_knots = boundary_knots, exclude_constant_splines = exclude_constant_splines) # assignation is unnecessary rigth @ TODO chekc
        out = model
    if L2 and inference:

        boot_lambdas = np.array([fit_I_spline_L2(y=np.random.choice(y, len(y), replace=True),
                                         x=np.random.choice(x, len(x), replace=True),
                                         k=k, interior_knots=interior_knots,
                                         boundary_knots=boundary_knots,
                                         exclude_constant_splines=exclude_constant_splines)['solution'] for _ in range(bootstrap_n)])

        inference_lambdas = {'se': np.apply_along_axis(sem, axis=0, arr=boot_lambdas),
                             'conf_int': np.apply_along_axis(lambda x: np.percentile(x, q=[2.5, 97.5]), axis=0, arr=boot_lambdas)
}

        boot_model = np.apply_along_axis(lambda l: I_spline(x, k, interior_knots, lambdas=l), axis=1, arr=boot_lambdas)
        inference_model = { 'conf_int': np.apply_along_axis(lambda x: np.percentile(x, q=[2.5, 97.5]), axis=0, arr=boot_model)
}

        out = {'model': model, 'inference_lambdas': inference_lambdas, 'inference_model': inference_model }
    return out

# I_spline and M_spline and depedencies