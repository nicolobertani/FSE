import warnings
import numpy as np

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

def M_basis(i, x, k, t):
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



def I_knots_sequence(k, interior_knots, boundary_knots = (0,1)):
    t = [min(boundary_knots)] * (k+1) + interior_knots + [max(boundary_knots)] * (k+1)
    return t


def I_basis(i, x, k, t):
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


# I_spline and M_spline and depedencies