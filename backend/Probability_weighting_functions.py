from scipy.stats import norm
import math
## probability weighting functions

x = 120
y = 10
pwfList = ("PW", "Prl1", "TK", "GE", "NeoA", "Prl2", "WG")
pwfList1par = ("PW", "Prl1", "TK")
pwfList2par = ("GE", "NeoA", "Prl2" ,"WG")
nLLPwfList = ("nLL.", "PW", "Prl1", "TK", "GE", "NeoA", "Prl2", "WG")
properNamesPwf = ("Power", "1-parameter Prelec", "Tversky-Kahneman", "Goldstein-Einhorn", "Neo-additive", "2-parameter Prelec", "Wu-Gonzalez")

def PW(x, r, *args):
    res = x ** r
    return res

def nLL_PW(parameters):
    sigma2, r = parameters
    input = norm.pdf(y, PW(x, r), math.sqrt(sigma2))
    res = sum(- (math.log(input)))
    return res

def par_PW(r):
    return sum((y - PW(x, r))) ** 2


def nLL_2lc_PW(parameters):
    sigma2, r1, r2, m1, m2 = parameters
    input = m1 * norm.pdf(y, PW(x,r1), math.sqrt(sigma2)) + \
            m2 * norm.pdf(y, PW(x,r2), math.sqrt(sigma2))
    return sum(-(math.log(input)))

def nLL_3lc_PW(parameters):
    sigma2, r1, r2, r3, m1, m2, m3 = parameters
    input = m1 * norm.pdf(y, PW(x,r1), math.sqrt(sigma2)) + \
            m2 * norm.pdf(y, PW(x,r2), math.sqrt(sigma2)) + \
            m3 * norm.pdf(y, PW(x,r3), math.sqrt(sigma2))
    return sum(-(math.log(input)))

def par_2lc_PW(parameters):
    r1, r2, m1, m2 = parameters
    return sum((y - (m1 * PW(x, r1) + m2 * PW(x,r2))) ** 2)

def par_3lc_PW(parameters):
    r1, r2, r3, m1, m2, m3 = parameters
    return sum((y - (m1 * PW(x, r1) + m2 * PW(x, r2) + m3 * PW(x, r3))) **2)

def Prl1(x, r, *args):
    return math.exp(-(- math.log(x) ** r))

def nLL_Prl1(parameters):
    sigma2, r = parameters
    input = norm.pdf(y, Prl1(x, r, s), math.sqrt(sigma2))
    return sum(- (math.log(input)))

def par_Prl1(r):
    sum((y - Prl1(x,r)) ** 2)

def nLL_2lc_Prl1(parameters):
    sigma2, r1, r2, m1, m2 = parameters
    input = m1 * norm.pdf(y, Prl1(x, r1), math.sqrt(sigma2)) + m2 * norm.pdf(y, Prl1(x, r2), math.sqrt(sigma2))
    return sum(- math.log(input))

def nLL_3lc_Prl1(parameters):
    sigma2,r1, r2, r3, m1, m2, m3 = parameters
    input = m1 * norm.pdf(y, Prl1(x, r1), math.sqrt(sigma2)) + m2 * norm.pdf(y, Prl1(x, r2), math.sqrt(sigma2)) + m3 * norm.pdf(y, Prl1(x, r3), math.sqrt(sigma2))
    return sum(- math.log(input))

def par_2lc_Prl1(parameters):
    r1, r2, m1, m2 = parameters
    return sum((y - (m1 * Prl1(x, r1) + m2 * Prl1(x, r2))) ** 2)

def par_3lc_Prl1(parameters):
    r1, r2, r3, m1, m2, m3 = parameters
    return sum((y - (m1 * Prl1(x, r1) + m2 * Prl1(x, r2) + m3 * Prl1(x, r3))) ** 2)

def TK(x, r, *args):
    return (x ** r) / (x ** r + (1 - x) ** r) ** (1 / r)

def nLL_TK(parameters):
    sigma2, r =  parameters

    input = norm.pdf(y, TK(x, r), math.sqrt(sigma2))
    return sum(- math.log(input))

def par_TK(r):
    return sum((y - TK(x, r)) ** 2)

def nLL_2lc_TK(parameters):
    sigma2, r1, r2, m1, m2 = parameters

    input = m1 * norm.pdf(y, TK(x, r1), math.sqrt(sigma2)) + m2 * norm.pdf(y, TK(x, r2), math.sqrt(sigma2))
    return sum(- math.log(input))

def nLL_3lc_TK(parameters):
    sigma2, r1, r2, r3, m1, m2, m3 = parameters

    input = m1 * norm.pdf(y, TK(x, r1), math.sqrt(sigma2)) + m2 * norm.pdf(y, TK(x, r2), math.sqrt(sigma2)) + m3 * norm.pdf(y, TK(x, r3), math.sqrt(sigma2))
    return sum(- math.log(input))

def par_2lc_TK(parameters):
    r1, r2, m1, m2 = parameters
    return sum((y - (m1 * TK(x, r1) + m2 * TK(x, r2))) ** 2)

def par_3lc_TK(parameters):
    r1, r2, r3, m1, m2, m3 = parameters

    return sum((y - (m1 * TK(x, r1) + m2 * TK(x, r2) + m3 * TK(x, r3))) ** 2)

def GE (x, r, s):
    return (s * x ** r) / (s * x ** r + (1 - x) ** r)

def nLL_GE(parameters):
    sigma2, r, s, = parameters

    input = norm.pdf(y, GE(x, r, s), math.sqrt(sigma2))
    return sum(- math.log(input))

def par_GE (parameters):
    r,s =  parameters

    return sum((y - GE(x, r, s)) ** 2)

def nLL_2lc_GE(parameters):
    sigma2, r1, r2, m1, m2, s1, s2 = parameters

    input = m1 * norm.pdf(y, GE(x, r1, s1), math.sqrt(sigma2)) + m2 * norm.pdf(y, GE(x, r2, s2), math.sqrt(sigma2))
    return sum(- math.log(input))

def nLL_3lc_GE(parameters):
    sigma2, r1, r2, r3, m1, m2, m3, s1, s2, s3  =  parameters
    input = m1 * norm.pdf(y, GE(x, r1, s1), math.sqrt(sigma2)) + m2 * norm.pdf(y, GE(x, r2, s2), math.sqrt(sigma2)) + m3 * norm.pdf(y, GE(x, r3, s3), math.sqrt(sigma2))
    return sum(- math.log(input))

def par_2lc_GE(parameters):
    r1, r2, m1, m2, s1, s2 = parameters
    return sum((y - (m1 * GE(x, r1, s1) + m2 * GE(x, r2, s2))) ** 2)

def par_3lc_GE(parameters):
    r1, r2, r3, m1, m2, m3, s1, s2, s3 = parameters
    return sum((y - (m1 * GE(x, r1, s1) + m2 * GE(x, r2, s2) + m3 * GE(x, r3, s3))) **2)

def NeoA(x, r, s):
    return r*x + s

def nLL_NeoA(parameters):
    sigma2, r, s  = parameters
    input = norm.pdf(y, NeoA(x, r, s), math.sqrt(sigma2))
    return sum(- math.log(input))

def par_NeoA(parameters):
    r, s = parameters
    return sum((y - NeoA(x, r, s)) ** 2)

def nLL_2lc_NeoA(parameters):
    sigma2, r1, r2, m1, m2, s1, s2 =  parameters
    input = m1 * norm.pdf(y, NeoA(x, r1, s1), math.sqrt(sigma2)) + m2 * norm.pdf(y, NeoA(x, r2, s2), math.sqrt(sigma2))
    return sum(- math.log(input))

def nLL_3lc_NeoA(parameters):
    sigma2, r1, r2, r3, m1, m2, m3, s1, s2, s3 = parameters
    input = m1 * norm.pdf(y, NeoA(x, r1, s1), math.sqrt(sigma2)) + \
            m2 * norm.pdf(y, NeoA(x, r2, s2), math.sqrt(sigma2)) + \
            m3 * norm.pdf(y, NeoA(x, r3, s3), math.sqrt(sigma2))
    return sum(- math.log(input))

def par_2lc_NeoA(parameters):
    r1, r2, m1, m2, s1, s2 = parameters
    return sum((y - (m1 * NeoA(x, r1, s1) + m2 * NeoA(x, r2, s2))) ** 2)

def par_3lc_NeoA(parameters):
    r1, r2, r3, m1, m2, m3, s1, s2, s3 = parameters
    return sum((y - (m1 * NeoA(x, r1, s1) + m2 * NeoA(x, r2, s2) + m3 * NeoA(x, r3, s3))) ** 2)

def Prl2(x, r, s):
    return math.exp(-s*(- math.log(x)) ** r)

def nLL_Prl2 (parameters):
    sigma2, r, s = parameters
    input = norm.pdf(y, Prl2(x, r, s), math.sqrt(sigma2))
    return sum(- math.log(input))

def par_Prl2(parameters):
    r, s = parameters
    return sum((y - Prl2(x, r, s)) ** 2)

def nLL_2lc_Prl2(parameters):
    sigma2, r1, r2, m1, m2, s1, s2 = parameters
    input = m1 * norm.pdf(y, Prl2(x, r1, s1), math.sqrt(sigma2)) + m2 * norm.pdf(y, Prl2(x, r2, s2), math.sqrt(sigma2))
    return sum(- math.log(input))

def nLL_3lc_Prl2(parameters):
    sigma2, r1, r2, r3, m1, m2, m3, s1, s2, s3 = parameters
    input = m1 * norm.pdf(y, Prl2(x, r1, s1), math.sqrt(sigma2)) + \
            m2 * norm.pdf(y, Prl2(x, r2, s2), math.sqrt(sigma2)) + \
            m3 * norm.pdf(y, Prl2(x, r3, s3), math.sqrt(sigma2))
    return sum(-math.log(input))

def par_2lc_Prl2 (parameters):
    r1, r2, m1, m2,  s1, s2 = parameters
    return sum((y - (m1 * Prl2(x, r1, s1) + m2 * Prl2(x, r2, s2))) ** 2)

def par_3lc_Prl2(parameters):
    r1, r2, r3, m1, m2, m3, s1, s2, s3 = parameters
    sum((y - (m1 * Prl2(x, r1, s1) + m2 * Prl2(x, r2, s2) + m3 * Prl2(x, r3, s3))) ** 2)

def WG(x, r, s):
    (x ** r) / (x ** r + (1 - x) ** r) ** s

def nLL_WG(parameters):
    sigma2, r, s =  parameters
    input = norm.pdf(y, WG(x, r, s), math.sqrt(sigma2))
    return sum(math.log(input))
def par_WG(parameters):
    r,s = parameters
    return sum((y - WG(x, r, s)) ** 2)

def nLL_2lc_WG(parameters):
    sigma2, r1, r2, m1, m2, s1, s2 = parameters
    input = m1 * norm.pdf(y, WG(x, r1, s1), math.sqrt(sigma2)) + \
            m2 * norm.pdf(y, WG(x, r2, s2), math.sqrt(sigma2))
    return sum(-math.log(input))

def nLL_3lc_WG(parameters):
    sigma2, r1, r2, r3, m1, m2, m3, s1, s2, s3 = parameters

    input = m1 * norm.pdf(y, WG(x, r1, s1), math.sqrt(sigma2)) + \
            m2 * norm.pdf(y, WG(x, r2, s2), math.sqrt(sigma2)) + \
            m3 * norm.pdf(y, WG(x, r3, s3), math.sqrt(sigma2))
    return sum(-math. log(input))

def par_2lc_WG(parameters):
    r1, r2, m1, m2, s1, s2 = parameters
    return sum((y - (m1 * WG(x, r1, s1) + m2 * WG(x, r2, s2))) ** 2)

def par_3lc_WG(parameters):
    r1, r2, r3, m1, m2, m3, s1, s2, s3 = parameters
    return sum((y - (m1 * WG(x, r1, s1) + m2 * WG(x, r2, s2) + m3 * WG(x, r3, s3))) ** 2)
