# FSE ---------------------------------------------------------------------

FSE.data <- jsonlite::read_json("~/OneDrive - ucp.pt/Github/FSE/results/FSE_0001.json", simplifyVector = TRUE)
chosen.xi <- c(.1, .9)
m <- 5
order <- 3

## representative shape ---------

sim.answers <- FSE.data$train_answers
X <- sim.answers$w_p - splines2::isp(sim.answers$p_x, knots = chosen.xi, Boundary.knots = c(0, 1), intercept = TRUE, df = m, degree = order - 1)
X <- X * sim.answers$s_tilde
## setup of constraints
D <- matrix(0, ncol(X), ncol(X))
diag(D) <- 1
positive_constraint_matrix <- 1 * D
d <- rep(0, unique(dim(D)))
A <- cbind(
  positive_constraint_matrix,
  t(X)
)
b <- c(
  rep(0, ncol(positive_constraint_matrix)),
  rep(1, nrow(X))
)
## solution
mod <- quadprog::solve.QP(D, d, A, b)
mod$normalized_solution <- mod$solution / sum(mod$solution)
mod$lambda_constraints <- mod$Lagrangian[1:m] > 0
mod$support_vectors <- mod$Lagrangian[-(1:m)] > 0

## plot ---------

plot(sim.answers$p_x, sim.answers$w_p, 
     col = c('red2', 'blue2')[sim.answers$s + 1],
     xlim = c(0, 1), ylim = c(0, 1), pch = 16)
curve(splines2::isp(x, knots = chosen.xi, Boundary.knots = c(0, 1), intercept = TRUE, df = m, degree = order - 1) %*% mod$normalized_solution, 
      from = 0, to = 1, add = TRUE, col = 'green2', lwd = 2)
abline(0, 1, lty = 2, col = 'grey')
points(FSE.data$test_answers$p_x, FSE.data$test_answers$w_p, 
       col = c('red2', 'blue2')[sim.answers$s + 1]
)


# bisection ---------------------------------------------------------------

bisection.data <- jsonlite::read_json("~/OneDrive - ucp.pt/Github/FSE/results/bisection_0001.json", simplifyVector = TRUE)
bisection.data$train_answers <- 
  bisection.data$train_answers %>% 
  mutate(w_p = (z - 2) / 16)

## representative shape -----------

negLL <- function(lambda) {
  - sum(s_i * (X %*% lambda) - log(1 + exp(X %*% (lambda))))
}

partial_dnegLL <- function(lambda, ordinal_for_lambda) {
  X[, ordinal_for_lambda] %*% (exp(X %*% (lambda)) / (1 + exp(X %*% (lambda))) - s_i)
}

dnegLL <- function(lambda) {
  sapply(seq(length(lambda)), partial_dnegLL, lambda = lambda)
}

sim.answers <- bisection.data$train_answers
X <- splines2::isp(sim.answers$p_x, knots = chosen.xi, Boundary.knots = c(0, 1), intercept = TRUE, df = m, degree = order - 1) - sim.answers$w_p
s_i <- sim.answers$s
## constraints
D <- matrix(0, ncol(X), ncol(X))
diag(D) <- -1
d <- rep(0, unique(dim(D)))
## constrained solution
mod <- constrOptim(rep(-1/m, m),
                   negLL,
                   grad = dnegLL,
                   ui = D,
                   ci = d,
                   method = "BFGS")
## archiving solutions
mod$solution <- zapsmall(mod$par / sum(mod$par))

## plot ---------

plot(sim.answers$p_x, sim.answers$w_p, 
     col = c('red2', 'blue2')[sim.answers$s + 1],
     xlim = c(0, 1), ylim = c(0, 1), pch = 16)
curve(splines2::isp(x, knots = chosen.xi, Boundary.knots = c(0, 1), intercept = TRUE, df = m, degree = order - 1) %*% mod$solution, 
      from = 0, to = 1, add = TRUE, col = 'green2', lwd = 2)
abline(0, 1, lty = 2, col = 'grey')
points(FSE.data$test_answers$p_x, FSE.data$test_answers$w_p, 
       col = c('red2', 'blue2')[sim.answers$s + 1]
)


# Bayesian LR -------------------------------------------------------------

bayesian.data <- jsonlite::read_json("~/OneDrive - ucp.pt/Github/FSE/results/Bayesian_0002.json", simplifyVector = TRUE)

## representative shape -------------

answer.data <- bayesian.data$train_answers
fit <- rstan::stan(
  file = '~/elicit/code/Bayesian_FSE/stan_models/LR_luce_gamma-pwf.stan',
  data = list(
    Q = nrow(answer.data),
    M = 5,
    wp = answer.data$w_p,
    X = as.matrix(splines2::isp(
      answer.data$p_x,
      knots = c(.1, .9),
      Boundary.knots = c(0, 1),
      intercept = TRUE,
      df = 5,
      degree = 2
    )),
    s = ifelse(answer.data$s, 0, 1)
  ),
  seed = 1
)
rstan::summary(fit)
draws <- rstan::extract(fit)
lambda.fit <- colMeans(draws$lambda)

## plot ---------

plot(answer.data$p_x, answer.data$w_p, 
     col = c('red2', 'blue2')[answer.data$s + 1],
     xlim = c(0, 1), ylim = c(0, 1), pch = 16)
curve(splines2::isp(x, knots = chosen.xi, Boundary.knots = c(0, 1), intercept = TRUE, df = m, degree = order - 1) %*% lambda.fit, 
      from = 0, to = 1, add = TRUE, col = 'green2', lwd = 2)
abline(0, 1, lty = 2, col = 'grey')
points(FSE.data$test_answers$p_x, FSE.data$test_answers$w_p, 
       col = c('red2', 'blue2')[sim.answers$s + 1]
)
