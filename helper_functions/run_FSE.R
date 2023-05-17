if (!require(quadprog)) install.packages('quadprog', dependencies = T, repos = 'cran.r-project.org')
library(quadprog)


run.FSE <- function(epsilon_threshold = .1) {
  
  # questioning ---------------------------------------------------------------
  
  # initialization for questions
  sim.answers <- data.frame(matrix(NA, nrow = 1, ncol = 5))
  colnames(sim.answers) <- c('p.x', 'z', 'w.p', 's', 's.tilde')
  epsilon <- Inf
  iteration <- 0
  # initialization for LPs
  A1 <- matrix(rep(rep(0, m), m), ncol = m)
  diag(A1) <- 1
  # bounds with no answers
  lower_bound <- I_spline(helper, order, interior_knots = chosen.xi, individual = T)[, m]
  upper_bound <- I_spline(helper, order, interior_knots = chosen.xi, individual = T)[, 1]
  D <- upper_bound - lower_bound
  # create storage for bounds
  bound.list <- list(
    rbind(
      lower_bound,
      upper_bound
    ))
  
  # {
  while (epsilon > epsilon_threshold) {
    iteration <- iteration + 1
    
    # find next p
    candidates <- D == max(D)
    ## checks whether more than one candidate for next p exists
    if (sum(candidates) == 1) { # if one point exists
      sim.answers[iteration, 1] <- helper[candidates]
    } else { # if multiple points exist
      warning('multiple optimal bisection points')    
      abs.distance.from.middle <- abs(helper[candidates] - .5)
      sim.answers[iteration, 1] <- tail(helper[candidates][abs.distance.from.middle == max(abs.distance.from.middle)], 1)
    }
    
    # compute next z and w.p
    w.p_t <- (upper_bound + lower_bound)[helper == sim.answers[iteration, 1]] / 2
    sim.answers[iteration, 2] <- w.p_t * (x - y) + y
    sim.answers[iteration, 3] <- w.p_t
      
    # asks the question and records the truth
    sim.answers[iteration, 4] <- defining.function(sim.answers[iteration, 1]) < sim.answers[iteration, 3]
    sim.answers[iteration, 5] <- ifelse(sim.answers[iteration, 4], 1, -1)
    
    # prepare parameters for LPs
    ## needs to be a matrix with M rows and a column per question
    if (iteration == 1) {
      A2 <- t(sim.answers$s.tilde * t(I_spline(sim.answers$p.x, order, interior_knots = chosen.xi, individual = T)))
    } else {
      A2 <- t(sim.answers$s.tilde * I_spline(sim.answers$p.x, order, interior_knots = chosen.xi, individual = T))
    }
    b <- c(1,
           rep(0, m),
           sim.answers$s.tilde * sim.answers$w.p
    )
    constraint_signs <- c("==", 
                          rep(">=", m),
                          rep("<=", nrow(sim.answers))
    )
    A <- t(cbind(
      rep(1, m),
      A1,
      A2
    ))
    
    ## calculate lower bound
    lower_bound <- sapply(helper, function(local.x) {
      c <- I_spline(local.x, 3, interior_knots = chosen.xi, individual = T)
      sol <- solveLP(c, b, A,
                     maximum = F,
                     const.dir = constraint_signs,
                     lpSolve = T)
      sol$solution %*% c
    })
    
    ## calculate upper bound
    upper_bound <- sapply(helper, function(local.x) {
      c <- I_spline(local.x, order, interior_knots = chosen.xi, individual = T)
      sol <- solveLP(c, b, A, 
                     maximum = T,
                     const.dir = constraint_signs,
                     lpSolve = T)
      sol$solution %*% c
    })
    
    ## calculate max difference based on updated bounds
    D <- upper_bound - lower_bound
    epsilon <- max(D)
    
    ## store bounds
    bound.list[[iteration + 1]] <- rbind(
        lower_bound,
        upper_bound
      )
  }
  

  # representative shape ----------------------------------------------------

  sim.answers$s <- sim.answers$s.tilde
  sim.answers$s.true <- sim.answers$s.tilde
  sim.answers$correct <- sim.answers$s == sim.answers$s.true
  X <- sim.answers$w.p - I_spline(sim.answers$p.x, order, interior_knots = chosen.xi, individual = T)
  X <- X * sim.answers$s
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
  mod <- solve.QP(D, d, A, b)
  mod$normalized_solution <- mod$solution / sum(mod$solution)
  mod$lambda_constraints <- mod$Lagrangian[1:m] > 0
  mod$support_vectors <- mod$Lagrangian[-(1:m)] > 0
  

  # output ------------------------------------------------------------------
  
  return(list(
    sim.answers, 
    rbind(lower_bound, upper_bound), 
    mod,
    bound.list
  ))
}
