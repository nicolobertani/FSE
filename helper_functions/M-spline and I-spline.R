##### --------------- M-spline and I-spline --------------------- ######


#### Setup ####

# install.packages("splines2")
# library(splines2)
# library(tidyverse)
# library(linprog)
# library(quadprog)
# setwd("/Volumes/HDD/Coco/Dropbox/Insead DB/Nicol\303\262 - Relevant literature/ELICIT EXPERIMENT/R code and deliverables")
# rm(list = ls())
# # # x <- sort(runif(100))
# # x <- seq(0,1, 0.01)
# # y <- sapply(1.2 * x + rnorm(length(x), 0, 0.2), function(x) {min(max(x,0),1)})
# # # e <- .000000000001
 

## Generata knots sequence for basis M_spline
M_knots_sequence <- function(k, interior_knots, boundary_knots = c(0,1)) {
  
  t <- c(rep(min(boundary_knots), k),
         interior_knots,
         rep(max(boundary_knots), k))
  
  return(t)
}

##### --------------- M-spline: create functions --------------------- ######

## Define basis M-spline
M_basis <- Vectorize(
  function(i, x, k, t) {
    
    if (i + k > length(t))
      stop("i + k > |t|.")
    
    if (x == 1)
      x <- 1 - ifelse("e" %in% ls(), e, .000000000001)
    
    out <- 
      if (k == 1) {
        
        if (x >= t[i] && x < t[i + 1]) {
          1 / (t[i + 1] - t[i])
        } else {
          0
        }
        
      } else {
        
        if (t[i + k] > t[i]) {
          (k  * 
             ((x - t[i]) * M_basis(i, x, k - 1, t) +
                (t[i + k] - x) * M_basis(i + 1, x, k - 1, t)))  / 
            ((k - 1) * (t[i + k] - t[i]))
        } else {
          0
        }
        
      }
    
    return(out)
  }, c("x"))



## Checks
# M_basis(6, x, 3, c(0, 0, 0, .1, .5, .9, 1, 1, 1))
# sapply(x, function(x) M_basis(1, x, 3, c(0, 0, 0, .1, .5, .9, 1, 1, 1)))
# sapply(1:6, function(i)  M_basis(i, x, 3, c(0, 0, 0, .1, .5, .9, 1, 1, 1)))
# apply(sapply(1:6, function(i) M_basis(i, x, 3, c(0, 0, 0, .1, .5, .9, 1, 1, 1))), 1, sum)


## Define combination of n M-splines ##
M_spline <- 
  function(x = 0, k, interior_knots, individual = F, boundary_knots = c(0,1), lambdas = NULL) {
    
    t <- M_knots_sequence(k, interior_knots, boundary_knots)
    m <- length(t) - k

    if(!(length(lambdas) %in% c(0, m)))
      stop(paste0("Incorrect number of lambdas. Need ", m, " lambdas."))
    if(length(lambdas) && individual)
       warning("lambdas are compatible with individual output.")
    if(!length(lambdas))
      lambdas <- rep(1/m, m)
    if(sum(lambdas) != 1)
      warning("Lambdas do not sum up to 1.")
    
    out <- 
      if(individual) {
        sapply(1:m, function(i) M_basis(i, x, k, t))
    } else {
      sapply(1:m, function(i) M_basis(i, x, k, t)) %*%
        lambdas
    }
    
    return(out)
  }


## Checks 
# head(M_spline(x, 3, c(.1, .5, .9), individual =  T))
# head(M_spline(x, 3, c(.1, .5, .9), individual =  F, lambdas = rep(1, 6)))
# head(M_spline(x, 3, c(.1, .5, .9), individual =  F))

# all.equal(sapply(1:6, function(i) M_basis(i, x, 3, c(0,0,0,.1,.5,.9,1,1,1))),
#           M_spline(x, 3, c(.1, .5, .9), individual =  T))
# all.equal(apply(sapply(1:6, function(i) M_basis(i, x, 3, c(0,0,0,.1,.5,.9,1,1,1))), 1, sum),
#           as.vector(M_spline(x, 3, c(.1, .5, .9), individual =  F, lambdas = rep(1, 6))))

# all.equal(as.vector(sapply(1:6, function(i) M_basis(i, x, 3, c(0,0,0,.1,.5,.9,1,1,1)))),
#           as.vector(mSpline(x, degree = 2, knots = c(.1, .5, .9), intercept = T)))


## Define regression function on M-splines ##
plot_M_spline <-  function(y, x = NULL, k, interior_knots, boundary_knots = c(0,1), 
                           point.type = 21, point.size = .8, point.color = gray(.2, .8), ...) {

  t <- M_knots_sequence(k, interior_knots, boundary_knots)
  m <- length(t) - k
  if(!length(x)) {
    y <- sort(y)
    x <- seq(0, 1, length.out = length(y))    
  }
  
  model_formula <- as.formula(paste0("y ~ ", paste("M_basis(", 1:m, ", x, k, t)", collapse = " + "), " + 0"))
  model <- lm(model_formula)
  
  plot(y ~ x,
       pch = point.type, cex = point.size, col = point.color, bg = gray(.5, .6), ...)
  points(sort(x), suppressWarnings(M_spline(x = sort(x), k = k, interior_knots = interior_knots, boundary_knots = boundary_knots, lambdas = model$coefficients)),
         type = "l", lwd = 2, col = rgb(0, .8, 0))
  abline(v = c(interior_knots, boundary_knots), lty = 2, col = gray(.2))
  
  return(model)
}

# plot_M_spline(y = y, x = x, k = 3, interior_knots = c(.1,.5,.9))

##### --------------- I-spline: create functions --------------------- ######
## Generata knots sequence for basis I_spline
I_knots_sequence <- function(k, interior_knots, boundary_knots = c(0,1)) {
  
  t <- c(rep(min(boundary_knots), k + 1),
    interior_knots,
    rep(max(boundary_knots), k + 1))
  
  return(t)
}



## Define basis I-spline ##
I_basis <- Vectorize(
  function(i, x, k, t) {
    
    if (!(i %in% 1:(length(t)-k)))
      stop("i > m = length(t) - k.")
    
    if (x == 1)
      x <- 1 - ifelse("e" %in% ls(), e, .000000000001)
    
    j <- seq(length(t)) %*% ((x >= t) & (x < c(t[2:length(t)], 1)))
    
    out <- if (i > j) {
      
      0
      
    } else {
      
      if (i < j - k + 1) {
        
        1
        
      } else {
        
        do.call(function(t, s, k) { (t[s+k+1] - t[s]) / (k + 1) }, list(t = t, s = i:j, k = k)) %*%
          sapply(i:j, function (i) M_basis(i, x = x, k = k + 1, t = t))
        
      }
    }
    
    return(out)
    
  }, "x")


## checks
# head(I_basis(2, x, 3, c(0,0,0,0,.1,.5,.9,1,1,1,1)))
# head(sapply(1:8, function(i) I_basis(i, x, 3, c(0,0,0,0,.1,.5,.9,1,1,1,1))))

# plot(1,0, xlim = c(0,1), ylim = c(0,1))
# sapply(1:8, function(i) {points(x, I_basis(i, x, 3, c(0,0,0,0,.1,.5,.9,1,1,1,1)), type = "l", col = i)})



## Define combination of n I-splines ##
I_spline <-
  function(x = 0, k, interior_knots, lambdas = NULL, individual = F, boundary_knots = c(0,1), exclude_constant_splines = T) {

    t <- I_knots_sequence(k, interior_knots, boundary_knots)
    m <- length(t) - k - ifelse(exclude_constant_splines, 2, 0)
    
    if(!(length(lambdas) %in% c(0, m)))
      stop(paste0("Incorrect number of lambdas. Need ", m, " lambdas."))
    if(length(lambdas) && individual)
      warning("lambdas are compatible with individual output.")
    if(!length(lambdas))
      lambdas <- rep(1/m, m)
    if(sum(lambdas) < .9999 || sum(lambdas) > 1.0001)
      warning("Lambdas do not sum up to 1.")
    
    i_sequence <- ifelse(exclude_constant_splines, 2, 1):ifelse(exclude_constant_splines, m+1, m)
    
    out <-
      if (individual) {
        sapply(i_sequence, function(i) I_basis(i, x, k, t))
      } else {
        sapply(i_sequence, function(i) I_basis(i, x, k, t))  %*%
          lambdas
      }
    
    return(out)
  }


## checks
# head(I_spline(x, 3, c(.1, .5, .9), individual = T))
# head(I_spline(x, 3, c(.1, .5, .9), lambdas = rep(1, 6)))
# head(I_spline(x, 3, c(.1, .5, .9)))

# all.equal(as.vector(sapply(2:7, function(i) I_basis(i, x, 3, c(0,0,0,0,.1,.5,.9,1,1,1,1)))),
#           as.vector(I_spline(x, 3, c(.1, .5, .9), individual = T)))
# all.equal(apply(I_spline(x, 3, c(.1, .5, .9), individual = T), 1, sum),
#           as.vector(I_spline(x, 3, c(.1, .5, .9), lambdas = rep(1, 6))))

# all.equal(as.vector(I_spline(x, 3, c(.1, .5, .9), individual = T)),
#           as.vector(iSpline(x, degree = 2, knots = c(.1, .5, .9), Boundary.knots = c(0,1), intercept = T)))



## Define regression function on I-splines using L2 ##
fit_I_spline_L2 <- 
  function(y, x, k, interior_knots, ...) {
    X <- I_spline(x = sort(x), k = k, individual = T, interior_knots = interior_knots,...)
    Dmat <- t(X) %*% X
    d <- t(X) %*% y
    Amat <- cbind(rep(1, unique(dim(Dmat))), diag(unique(dim(Dmat))))
    b <- c(1, rep(0, unique(dim(Dmat))))
    out <- solve.QP(Dmat = Dmat, dvec = d, Amat = Amat, b, meq = 1)
    out
  }

## Checks
# fit_I_spline_L2(y, x=x, k = 3, c(.1, .5, .9))
# lbs <- fit_I_spline_L2(y, x=x, k = 3, c(.1, .5, .9))$solution
# plot(y~x)
# lines(x, I_spline(x, 3, interior_knots = c(.1, .5, .9), lambdas = lbs))


## Define regression function on I-splines using L1 ##


# General fitting function with bootstrapping
fit_I_spline <- function(y = NULL, x = NULL, k, interior_knots, boundary_knots = c(0,1), exclude_constant_splines = T, # I-spline arguments
                         L2 = T, inference = F, bootstrap_n = 100, # fitting arguments
                         point.type = 21, point.size = .8, point.color = gray(.2, .8), ...) { # graphical arguments
  
  if(length(y) != length(x))
    stop("x and y need to be of the same length.")
  if(!length(x)) {
    y <- sort(y)
    x <- seq(0, 1, length.out = length(y))}
  if(L2 && !("package:quadprog" %in% search()))
    require(quadprog, quietly = T)
  
  if(L2) {
    model <- fit_I_spline_L2(y, x, k, interior_knots, 
                             boundary_knots = boundary_knots, exclude_constant_splines = exclude_constant_splines)
    out <- model
  }

  if(L2 && inference) {
    boot_lambdas <- sapply(seq(bootstrap_n), function(...) {
      boot_obs <- cbind(y, x)[sort(sample(seq(length(y)), length(y), replace = T)), ] # generate bootstrap sample
      
      fit_I_spline_L2(y = boot_obs[, 1], x = boot_obs[, 2], k, interior_knots, # fit I-spline to bootstrap sample
                      boundary_knots = boundary_knots, exclude_constant_splines = exclude_constant_splines)$solution
    })
    inference_lambdas <- list(
      se = apply(boot_lambdas, 1, sd),
      conf_int = apply(boot_lambdas, 1, quantile, probs = c(.025, .975))
      )
    boot_model <- 
      apply(boot_lambdas, 2, function (l) {I_spline(x, k, interior_knots, lambdas = l)}) # predict and return percentage points from fitted I-spline
    inference_model <- list(
      conf_int = apply(boot_model, 1, quantile, probs = c(.025, .975))
    )
    out <- list(model = model, inference_lambdas = inference_lambdas, inference_model = inference_model)
  }
  
  return(out)
}

# temp <- fit_I_spline(y, x, k = 3, c(.1, .5, .9), inference = T, bootstrap_n = 100)
# temp
# plot(y ~ x)
# lines(x, I_spline(x, 3, interior_knots = c(.1, .5, .9), lambdas = temp$model$solution), col = 3, lwd = 2)
# lines(x, temp$inference_model$conf_int[1,],
#       col = 3, lty = 3, lwd = 2)
# lines(x, temp$inference_model$conf_int[2,],
#       col = 3, lty = 3, lwd = 2)


# mx <- matrix(rep(rep(0, length(x)), length(x)), ncol = length(x))
# diag(mx) <- I_spline(x, 3, c(.1, .5, .9), individual = T)[,1] + 
#   I_spline(x, 3, c(.1, .5, .9), individual = T)[,2]
# mx
# persp(x, x, mx)


