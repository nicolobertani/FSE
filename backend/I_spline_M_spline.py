import warnings
import numpy as np


def calc_basis(t, s, k):
    return (t[s+k+1] - t[s]) / (k + 1)

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
    #m = len(t) - k
    m,= 5 #@TODO check correct
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


def I_basis(i, x, k, t): # @ TODO here is the issue, I want to vectorize it but i am not sure how to it
    if not (i in range(1, len(t)-k+1)):
        raise ValueError("i > m = length(t) - k.")
    #if x == 1:
    #    x = 1 - (np.e if 'e' in locals() else 0.000000000001)

    #x = np.array(x)  # Convert x to a NumPy array if it's not already
    #t = np.array(t)  # Convert t to a NumPy array if it's not already

    j = np.sum((((x[:, None] >= t) & (x[:, None] < np.concatenate((t[1:], [1]))))), axis=1)
    print("j", j)
    print("i", i)

    if np.all(i > j): #@ TODO is what we want??
        out = 0

    #out = np.where(i > j, 0, np.empty_like(j)) # @TODO or this
    #if True:
    #    pass
    elif i < j - k + 1:
            out = 1
    else:
        out = np.matmul(
            calc_basis(t, np.arange(i, j+1), k),
            np.apply_along_axis(lambda i: M_basis(i, x=x, k=k+1, t=t), axis=1, arr=np.arange(i, j+1))
        )

    return out

def I_spline(k, interior_knots, x=0, lambdas=None, individual=False, boundary_knots = (0,1), exclude_constant_splines = True):
    t = I_knots_sequence(k, interior_knots, boundary_knots)
    value = 2
    if not exclude_constant_splines:
        value = 0
    m = len(t) - k - value
    print("lambdas", lambdas )
    if lambdas not in (None,m):
        raise ValueError("Incorrect number of lambdas. Need ", m, " lambdas.")
    if lambdas and individual:
        warnings.warn("lambdas are compatible with individual output.")
    if not lambdas:
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

# test
import numpy as np
# Generate sorted random values
x = np.sort(np.random.rand(100))
# Generate a sequence from 0 to 1 with a step of 0.01
x = np.arange(0, 1.01, 0.01)
print("x", x)
# Calculate y values using a lambda function
y = np.array([min(max(1.2 * xi + np.random.normal(0, 0.2), 0), 1) for xi in x])
# Set the value of e
e = 1e-12


print("output", I_basis(2, x, 3, (0,0,0,0,.1,.5,.9,1,1,1,1)))

#I_spline(x=x, k=3, interior_knots=[.1, .5, .9], individual = True)