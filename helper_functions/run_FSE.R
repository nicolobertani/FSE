if (!require(quadprog)) install.packages('quadprog', dependencies = T, repos = 'cran.r-project.org')
library(quadprog)


run.FSE <- function(epsilon_threshold = .1, error = 0, error.model = 'noisy valuation') {
  
  if (!error.model %in% c('noisy valuation', 'random mistakes')) stop('Wrong error model!')

  # questioning ---------------------------------------------------------------
  
  sim.answers <- data.frame(matrix(NA, nrow = 1, ncol = 5))
  colnames(sim.answers) <- c('p.x', 'z', 'w.p', 's', 's.true')
  epsilon <- Inf
  iteration <- 0
  A1 <- matrix(rep(rep(0, m), m), ncol = m)
  diag(A1) <- 1
  lower_bound <- I_spline(helper, order, interior_knots = chosen.xi, individual = T)[, m]
  upper_bound <- I_spline(helper, order, interior_knots = chosen.xi, individual = T)[, 1]
  bound.list <- list(
    rbind(
      lower_bound,
      upper_bound
    ))
  
  # {
  while (epsilon > epsilon_threshold) {
    iteration <- iteration + 1
    
    if (iteration == 1) {
      
      sim.answers[iteration, 1] <- .9
      sim.answers[iteration, 2] <- 65
      sim.answers[iteration, 3] <- ((sim.answers[iteration, 2] - y) / (x - y))
      
    } else {
      
      D <- upper_bound - lower_bound
      new.w.p <- ((upper_bound + lower_bound)[D == max(D)] / 2)[1]
      
      if (length(D[D == max(D)]) == 1) {
        sim.answers[iteration, 1] <- helper[D == max(D)]
      } else {
        warning('multiple optimal bisection points')      
        sim.answers[iteration, 1] <- helper[D == max(D)][which.max(abs(helper[D == max(D)] - .5))]
      }
      sim.answers[iteration, 2] <- (new.w.p) * (x - y) + y
      sim.answers[iteration, 3] <- new.w.p
    }
    
    sim.answers[iteration, 5] <- defining.function(sim.answers[iteration, 1]) < sim.answers[iteration, 3]
    
    if (error.model == 'noisy valuation') {
      sim.answers[iteration, 4] <- 
        defining.function(sim.answers[iteration, 1]) + rnorm(1, 0, error) < sim.answers[iteration, 3]
    } else {
      sim.answers[iteration, 4] <- 
        ifelse(rbinom(1, 1, error), !sim.answers[iteration, 5], sim.answers[iteration, 5])
    }
    
    ## update upper and lower bounds  
    input_lower <- sim.answers[sim.answers$s == 0, ]
    input_upper <- sim.answers[sim.answers$s == 1, ]
    
    ## both positive number of constraints
    if(nrow(input_lower) != 0 && nrow(input_upper) != 0) {
      A2 <- t(rbind(I_spline(input_lower$p.x, order, interior_knots = chosen.xi, individual = T),
                    I_spline(input_upper$p.x, order, interior_knots = chosen.xi, individual = T)))
      
      b <- c(1,
             rep(0, m),
             input_lower$w.p,
             input_upper$w.p
      )
      
      constraint_signs <- c("==", 
                            rep(">=", m),
                            rep(">=", length(input_lower$w.p)),
                            rep("<=", length(input_upper$w.p)))
    }
    
    ## if no lower bound constraints
    if(nrow(input_lower) == 0 && nrow(input_upper) != 0) {
      A2 <- t(I_spline(input_upper$p.x, order, interior_knots = chosen.xi, individual = T))
      
      b <- c(1,
             rep(0, m),
             input_upper$w.p
      )
      
      constraint_signs <- c("==", 
                            rep(">=", m),
                            rep("<=", length(input_upper$w.p)))
      
      lower_bound <- I_spline(helper, order, interior_knots = chosen.xi, individual = T)[, m]
    }
    
    ## if no upper bound constraints
    if(nrow(input_lower) != 0 && nrow(input_upper) == 0) {
      A2 <- t(I_spline(input_lower$p.x, order, interior_knots = chosen.xi, individual = T))
      
      b <- c(1,
             rep(0, m),
             input_lower$w.p
      )
      
      constraint_signs <- c("==", 
                            rep(">=", m),
                            rep(">=", length(input_lower$w.p)))
      
      upper_bound <- I_spline(helper, order, interior_knots = chosen.xi, individual = T)[, 1]
    }
    
    if(1 %in% dim(A2)) A2 <- t(A2)
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

  sim.answers$s <- ifelse(sim.answers$s == 1, 1, -1)
  sim.answers$s.true <- ifelse(sim.answers$s.true == 1, 1, -1)
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
