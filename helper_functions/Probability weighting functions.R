## Probability weighting functions

pwf_list <- c("PW", "Prl1", "TK", "GE", "NeoA", "Prl2", "WG")
pwf_list_1par <- c("PW", "Prl1", "TK")
pwf_list_2par <- c("GE", "NeoA", "Prl2" ,"WG")
nLL_pwf_list <- paste0("nLL.", pwf_list)
proper_names_pwf <- c("Power", "1-parameter Prelec", "Tversky-Kahneman", "Goldstein-Einhorn", "Neo-additive", "2-parameter Prelec", "Wu-Gonzalez")

# Power function - 1-parameter -----------
PW <- function(x, r, ...) {
  x^r
}

nLL.PW <- function(parameters) {
  sigma2 <- parameters[1]
  r <- parameters[2]
  input <- dnorm(y, PW(x, r), sqrt(sigma2))
  sum(-log(input))
}

par.PW <-  function(r) {
  sum((y - PW(x, r)) ^ 2)
}

nLL.2lc.PW <- function(parameters) {
  sigma2 <- parameters[1]
  r1 <- parameters[2]
  r2 <- parameters[3]
  m1 <- parameters[4]
  m2 <- parameters[5]
  input <-
    m1 * dnorm(y, PW(x, r1), sqrt(sigma2)) + 
    m2 * dnorm(y, PW(x, r2), sqrt(sigma2)) 
  sum(-log(input))
}

nLL.3lc.PW <- function(parameters) {
  sigma2 <- parameters[1]
  r1 <- parameters[2]
  r2 <- parameters[3]
  r3 <- parameters[4]
  m1 <- parameters[5]
  m2 <- parameters[6]
  m3 <- parameters[7]
  input <-
    m1 * dnorm(y, PW(x, r1), sqrt(sigma2)) + 
    m2 * dnorm(y, PW(x, r2), sqrt(sigma2)) + 
    m3 * dnorm(y, PW(x, r3), sqrt(sigma2)) 
  sum(-log(input))
}

par.2lc.PW <- function(parameters) {
  r1 <- parameters[1]
  r2 <- parameters[2]
  m1 <- parameters[3]
  m2 <- parameters[4]
  sum((y - (m1 * PW(x, r1) + m2 * PW(x, r2)))^2)
}
  
par.3lc.PW <- function(parameters) {
  r1 <- parameters[1]
  r2 <- parameters[2]
  r3 <- parameters[3]
  m1 <- parameters[4]
  m2 <- parameters[5]
  m3 <- parameters[6]
  sum((y - (m1 * PW(x, r1) + m2 * PW(x, r2) + m3 * PW(x, r3)))^2)
}

# Prelec - 1-parameter ----------
Prl1 <- function(x, r, ...) {
  exp(-(-log(x))^r)
}

nLL.Prl1 <- function(parameters) {
  sigma2 <- parameters[1]
  r <- parameters[2]
  input <- dnorm(y, Prl1(x, r, s), sqrt(sigma2))
  sum(-log(input))
}

par.Prl1 <-  function(r) {
  sum((y - Prl1(x, r)) ^ 2)
}

nLL.2lc.Prl1 <- function(parameters) {
  sigma2 <- parameters[1]
  r1 <- parameters[2]
  r2 <- parameters[3]
  m1 <- parameters[4]
  m2 <- parameters[5]
  input <-
    m1 * dnorm(y, Prl1(x, r1), sqrt(sigma2)) + 
    m2 * dnorm(y, Prl1(x, r2), sqrt(sigma2)) 
  sum(-log(input))
}

nLL.3lc.Prl1 <- function(parameters) {
  sigma2 <- parameters[1]
  r1 <- parameters[2]
  r2 <- parameters[3]
  r3 <- parameters[4]
  m1 <- parameters[5]
  m2 <- parameters[6]
  m3 <- parameters[7]
  input <-
    m1 * dnorm(y, Prl1(x, r1), sqrt(sigma2)) + 
    m2 * dnorm(y, Prl1(x, r2), sqrt(sigma2)) + 
    m3 * dnorm(y, Prl1(x, r3), sqrt(sigma2)) 
  sum(-log(input))
}

par.2lc.Prl1 <- function(parameters) {
  r1 <- parameters[1]
  r2 <- parameters[2]
  m1 <- parameters[3]
  m2 <- parameters[4]
  sum((y - (m1 * Prl1(x, r1) + m2 * Prl1(x, r2)))^2)
}

par.3lc.Prl1 <- function(parameters) {
  r1 <- parameters[1]
  r2 <- parameters[2]
  r3 <- parameters[3]
  m1 <- parameters[4]
  m2 <- parameters[5]
  m3 <- parameters[6]
  sum((y - (m1 * Prl1(x, r1) + m2 * Prl1(x, r2) + m3 * Prl1(x, r3)))^2)
}

# Tversky-Kahneman - 1-parameter ----------
TK <- function(x, r, ...) {
  (x ^ r) / (x ^ r + (1 - x) ^ r) ^ (1 / r)
}

nLL.TK <- function(parameters) {
  sigma2 <- parameters[1]
  r <- parameters[2]
  input <- dnorm(y, TK(x, r), sqrt(sigma2))
  sum(-log(input))
}

par.TK <-  function(r) {
  sum((y - TK(x, r)) ^ 2)
}

nLL.2lc.TK <- function(parameters) {
  sigma2 <- parameters[1]
  r1 <- parameters[2]
  r2 <- parameters[3]
  m1 <- parameters[4]
  m2 <- parameters[5]
  input <-
    m1 * dnorm(y, TK(x, r1), sqrt(sigma2)) + 
    m2 * dnorm(y, TK(x, r2), sqrt(sigma2)) 
  sum(-log(input))
}

nLL.3lc.TK <- function(parameters) {
  sigma2 <- parameters[1]
  r1 <- parameters[2]
  r2 <- parameters[3]
  r3 <- parameters[4]
  m1 <- parameters[5]
  m2 <- parameters[6]
  m3 <- parameters[7]
  input <-
    m1 * dnorm(y, TK(x, r1), sqrt(sigma2)) + 
    m2 * dnorm(y, TK(x, r2), sqrt(sigma2)) + 
    m3 * dnorm(y, TK(x, r3), sqrt(sigma2)) 
  sum(-log(input))
}

par.2lc.TK <- function(parameters) {
  r1 <- parameters[1]
  r2 <- parameters[2]
  m1 <- parameters[3]
  m2 <- parameters[4]
  sum((y - (m1 * TK(x, r1) + m2 * TK(x, r2)))^2)
}

par.3lc.TK <- function(parameters) {
  r1 <- parameters[1]
  r2 <- parameters[2]
  r3 <- parameters[3]
  m1 <- parameters[4]
  m2 <- parameters[5]
  m3 <- parameters[6]
  sum((y - (m1 * TK(x, r1) + m2 * TK(x, r2) + m3 * TK(x, r3)))^2)
}

# Goldstein-Einhorn - 2-parameter -------------
GE <- function(x, r, s) {
  (s * x ^ r) / (s * x ^ r + (1 - x) ^ r)
}

nLL.GE <- function(parameters) {
  sigma2 <- parameters[1]
  r <- parameters[2]
  s <- parameters[3]
  input <- dnorm(y, GE(x, r, s), sqrt(sigma2))
  sum(-log(input))
}

par.GE <-  function(params) {
  r <- params[1]
  s <- params[2]
  sum((y - GE(x, r, s)) ^ 2)
}

nLL.2lc.GE <- function(parameters) {
  sigma2 <- parameters[1]
  r1 <- parameters[2]
  r2 <- parameters[3]
  m1 <- parameters[4]
  m2 <- parameters[5]
  s1 <- parameters[6]
  s2 <- parameters[7]
  input <-
    m1 * dnorm(y, GE(x, r1, s1), sqrt(sigma2)) + 
    m2 * dnorm(y, GE(x, r2, s2), sqrt(sigma2)) 
  sum(-log(input))
}

nLL.3lc.GE <- function(parameters) {
  sigma2 <- parameters[1]
  r1 <- parameters[2]
  r2 <- parameters[3]
  r3 <- parameters[4]
  m1 <- parameters[5]
  m2 <- parameters[6]
  m3 <- parameters[7]
  s1 <- parameters[8]
  s2 <- parameters[9]
  s3 <- parameters[10]
  input <-
    m1 * dnorm(y, GE(x, r1, s1), sqrt(sigma2)) + 
    m2 * dnorm(y, GE(x, r2, s2), sqrt(sigma2)) + 
    m3 * dnorm(y, GE(x, r3, s3), sqrt(sigma2)) 
  sum(-log(input))
}

par.2lc.GE <- function(parameters) {
  r1 <- parameters[1]
  r2 <- parameters[2]
  m1 <- parameters[3]
  m2 <- parameters[4]
  s1 <- parameters[5]
  s2 <- parameters[6]
  sum((y - (m1 * GE(x, r1, s1) + m2 * GE(x, r2, s2)))^2)
}

par.3lc.GE <- function(parameters) {
  r1 <- parameters[1]
  r2 <- parameters[2]
  r3 <- parameters[3]
  m1 <- parameters[4]
  m2 <- parameters[5]
  m3 <- parameters[6]
  s1 <- parameters[7]
  s2 <- parameters[8]
  s3 <- parameters[9]
  sum((y - (m1 * GE(x, r1, s1) + m2 * GE(x, r2, s2) + m3 * GE(x, r3, s3)))^2)
}

# Neo-additive - 2-parameter ------------
NeoA <- function(x, r, s) {
  r*x + s
}

nLL.NeoA <- function(parameters) {
  sigma2 <- parameters[1]
  r <- parameters[2]
  s <- parameters[3]
  input <- dnorm(y, NeoA(x, r, s), sqrt(sigma2))
  sum(-log(input))
}

par.NeoA <-  function(params) {
  r <- params[1]
  s <- params[2]
  sum((y - NeoA(x, r, s)) ^ 2)
}

nLL.2lc.NeoA <- function(parameters) {
  sigma2 <- parameters[1]
  r1 <- parameters[2]
  r2 <- parameters[3]
  m1 <- parameters[4]
  m2 <- parameters[5]
  s1 <- parameters[6]
  s2 <- parameters[7]
  input <-
    m1 * dnorm(y, NeoA(x, r1, s1), sqrt(sigma2)) + 
    m2 * dnorm(y, NeoA(x, r2, s2), sqrt(sigma2)) 
  sum(-log(input))
}

nLL.3lc.NeoA <- function(parameters) {
  sigma2 <- parameters[1]
  r1 <- parameters[2]
  r2 <- parameters[3]
  r3 <- parameters[4]
  m1 <- parameters[5]
  m2 <- parameters[6]
  m3 <- parameters[7]
  s1 <- parameters[8]
  s2 <- parameters[9]
  s3 <- parameters[10]
  input <-
    m1 * dnorm(y, NeoA(x, r1, s1), sqrt(sigma2)) + 
    m2 * dnorm(y, NeoA(x, r2, s2), sqrt(sigma2)) + 
    m3 * dnorm(y, NeoA(x, r3, s3), sqrt(sigma2)) 
  sum(-log(input))
}

par.2lc.NeoA <- function(parameters) {
  r1 <- parameters[1]
  r2 <- parameters[2]
  m1 <- parameters[3]
  m2 <- parameters[4]
  s1 <- parameters[5]
  s2 <- parameters[6]
  sum((y - (m1 * NeoA(x, r1, s1) + m2 * NeoA(x, r2, s2)))^2)
}

par.3lc.NeoA <- function(parameters) {
  r1 <- parameters[1]
  r2 <- parameters[2]
  r3 <- parameters[3]
  m1 <- parameters[4]
  m2 <- parameters[5]
  m3 <- parameters[6]
  s1 <- parameters[7]
  s2 <- parameters[8]
  s3 <- parameters[9]
  sum((y - (m1 * NeoA(x, r1, s1) + m2 * NeoA(x, r2, s2) + m3 * NeoA(x, r3, s3)))^2)
}

# Prelec - 2-parameters ----------
Prl2 <- function(x, r, s) {
  exp(-s*(-log(x))^r)
}

nLL.Prl2 <- function(parameters) {
  sigma2 <- parameters[1]
  r <- parameters[2]
  s <- parameters[3]
  input <- dnorm(y, Prl2(x, r, s), sqrt(sigma2))
  sum(-log(input))
}

par.Prl2 <-  function(params) {
  r <- params[1]
  s <- params[2]
  sum((y - Prl2(x, r, s)) ^ 2)
}

nLL.2lc.Prl2 <- function(parameters) {
  sigma2 <- parameters[1]
  r1 <- parameters[2]
  r2 <- parameters[3]
  m1 <- parameters[4]
  m2 <- parameters[5]
  s1 <- parameters[6]
  s2 <- parameters[7]
  input <-
    m1 * dnorm(y, Prl2(x, r1, s1), sqrt(sigma2)) + 
    m2 * dnorm(y, Prl2(x, r2, s2), sqrt(sigma2)) 
  sum(-log(input))
}

nLL.3lc.Prl2 <- function(parameters) {
  sigma2 <- parameters[1]
  r1 <- parameters[2]
  r2 <- parameters[3]
  r3 <- parameters[4]
  m1 <- parameters[5]
  m2 <- parameters[6]
  m3 <- parameters[7]
  s1 <- parameters[8]
  s2 <- parameters[9]
  s3 <- parameters[10]
  input <-
    m1 * dnorm(y, Prl2(x, r1, s1), sqrt(sigma2)) + 
    m2 * dnorm(y, Prl2(x, r2, s2), sqrt(sigma2)) + 
    m3 * dnorm(y, Prl2(x, r3, s3), sqrt(sigma2)) 
  sum(-log(input))
}

par.2lc.Prl2 <- function(parameters) {
  r1 <- parameters[1]
  r2 <- parameters[2]
  m1 <- parameters[3]
  m2 <- parameters[4]
  s1 <- parameters[5]
  s2 <- parameters[6]
  sum((y - (m1 * Prl2(x, r1, s1) + m2 * Prl2(x, r2, s2)))^2)
}

par.3lc.Prl2 <- function(parameters) {
  r1 <- parameters[1]
  r2 <- parameters[2]
  r3 <- parameters[3]
  m1 <- parameters[4]
  m2 <- parameters[5]
  m3 <- parameters[6]
  s1 <- parameters[7]
  s2 <- parameters[8]
  s3 <- parameters[9]
  sum((y - (m1 * Prl2(x, r1, s1) + m2 * Prl2(x, r2, s2) + m3 * Prl2(x, r3, s3)))^2)
}
# Wu-Gonzalez - 2-parameter ---------
WG <- function(x, r, s) {
  (x ^ r) / (x ^ r + (1 - x) ^ r) ^ s
}

nLL.WG <- function(parameters) {
  sigma2 <- parameters[1]
  r <- parameters[2]
  s <- parameters[3]
  input <- dnorm(y, WG(x, r, s), sqrt(sigma2))
  sum(-log(input))
}

par.WG <-  function(params) {
  r <- params[1]
  s <- params[2]
  sum((y - WG(x, r, s)) ^ 2)
}

nLL.2lc.WG <- function(parameters) {
  sigma2 <- parameters[1]
  r1 <- parameters[2]
  r2 <- parameters[3]
  m1 <- parameters[4]
  m2 <- parameters[5]
  s1 <- parameters[6]
  s2 <- parameters[7]
  input <-
    m1 * dnorm(y, WG(x, r1, s1), sqrt(sigma2)) + 
    m2 * dnorm(y, WG(x, r2, s2), sqrt(sigma2)) 
  sum(-log(input))
}

nLL.3lc.WG <- function(parameters) {
  sigma2 <- parameters[1]
  r1 <- parameters[2]
  r2 <- parameters[3]
  r3 <- parameters[4]
  m1 <- parameters[5]
  m2 <- parameters[6]
  m3 <- parameters[7]
  s1 <- parameters[8]
  s2 <- parameters[9]
  s3 <- parameters[10]
  input <-
    m1 * dnorm(y, WG(x, r1, s1), sqrt(sigma2)) + 
    m2 * dnorm(y, WG(x, r2, s2), sqrt(sigma2)) + 
    m3 * dnorm(y, WG(x, r3, s3), sqrt(sigma2)) 
  sum(-log(input))
}

par.2lc.WG <- function(parameters) {
  r1 <- parameters[1]
  r2 <- parameters[2]
  m1 <- parameters[3]
  m2 <- parameters[4]
  s1 <- parameters[5]
  s2 <- parameters[6]
  sum((y - (m1 * WG(x, r1, s1) + m2 * WG(x, r2, s2)))^2)
}

par.3lc.WG <- function(parameters) {
  r1 <- parameters[1]
  r2 <- parameters[2]
  r3 <- parameters[3]
  m1 <- parameters[4]
  m2 <- parameters[5]
  m3 <- parameters[6]
  s1 <- parameters[7]
  s2 <- parameters[8]
  s3 <- parameters[9]
  sum((y - (m1 * WG(x, r1, s1) + m2 * WG(x, r2, s2) + m3 * WG(x, r3, s3)))^2)
}
