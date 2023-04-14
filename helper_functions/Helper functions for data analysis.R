##### Blank graph for probability square
s <- function (...) {plot(c(0,1), c(0,1),
                       type = "l", col = gray(.5), lty = "dashed",
                       xlab = NA,
                       ylab = NA,
                       ylim = c(0,1),
                       xlim = c(0,1),
                       cex.axis = .8,
                       cex.lab = .9,
                       ...)
}




##### Kolmogorov - Smirnov test for estimated pwfs using I-splines
ks_pvalue <- function (subject, 
                       which_solutions = "lr_solutions", compare_to = NULL, 
                       weight = "standard", x_points = "standard") {
  if(!(which_solutions %in% c("lr_solutions", "logistic_solutions", "svm_solutions"))) {
    warning("Wrong specification for which solution.")
    break
  }
  
  x <- 
    if (x_points == "standard") {
      answers[answers$n == subject, ]$p.x
    } else {
      seq(.05, .95, by = .05)
    }
  
  solutions_name <-
    if (which_solutions == "lr_solutions") {
      "solution"
    } else {
      "normalized_solution"
    }
  
  I <- eval(substitute(I_spline(x, order, chosen.xi, lambdas = get(a)[[b]]$d),
                       list(a = which_solutions, b = subject, d = solutions_name)))
  
  if (!length(compare_to)) {
    
    D <- unique(max(abs(I - punif(x))))
    
    d <- if (weight == "standard") {
      sqrt(length(x)) * D
    } else {
      (sqrt(length(x)) + .12 + .11/sqrt(length(x))) * D
    }
    
    k <- 0
    last_value <- 1
    ks_prob <- 0
    while (abs(last_value) > .000001) {
      k <- k + 1
      last_value <- (-1)^(k-1) * exp(-2 * k^2 * d^2)
      ks_prob <- ks_prob + last_value
    }
    
    return(list(
      I_spline = I,
      D = D,
      n = length(x),
      "wD" = d,
      p_value = 2 * ks_prob))
    
  } else {
    
    solutions_name2 <-
      if (compare_to == "lr_solutions") {
        "solution"
      } else {
        "normalized_solution"
      }
    
    I2 <- eval(substitute(I_spline(x, order, chosen.xi, lambdas = get(a)[[b]]$d),
                          list(a = compare_to, b = subject, d = solutions_name2)))
    
    D <- unique(max(abs(I - I2)))
    
    d <- if (weight == "standard") {
      sqrt(length(x)^2 / (2 * length(x))) * D
    } else {
      (sqrt(length(x)^2 / (2 * length(x))) + .12 + .11/sqrt(length(x)^2 / (2 * length(x)))) * D
    }
    
    k <- 0
    last_value <- 1
    ks_prob <- 0
    while (abs(last_value) > .0001) {
      k <- k + 1
      last_value <- (-1)^(k-1) * exp(-2 * k^2 * d^2)
      ks_prob <- ks_prob + last_value
    }
    
    return(list(
      I_splines = cbind(I, I2),
      D = D,
      n = length(x),
      "wD" = d,
      p_value = 2 * ks_prob))
  }
}




####### Bounding function using I-splines 
find.bounds <- function(subject, bound = "both") {
  if (!bound %in% c("both", "lower", "upper")) stop("Invalid bound: either both, lower, or upper.")
  ## general elements
  A1 <- matrix(rep(rep(0, m), m), ncol = m)
  diag(A1) <- 1
  # input <- answers[answers$n == 5, ]
  input <- answers[answers$n == subject, ]
  input_lower <- input[input$choose.sure == 0, ]
  input_upper <- input[input$choose.sure == 1, ]
  
  ## create constraint vector and signs depending on number of constraints per type (i.e. sure amount or lottery)
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
    
    lower_bound <- I_spline(seq(.01, .99, by = .01), order, interior_knots = chosen.xi, individual = T)[, m]
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
    
    upper_bound <- I_spline(seq(.01, .99, by = .01), order, interior_knots = chosen.xi, individual = T)[, 1]
  }
  
  A <- t(cbind(
    rep(1, m),
    A1,
    A2
  ))
  
  ## calculate lower bound
  if (bound %in% c("both", "lower") && nrow(input_lower) != 0) {
    lower_bound <- sapply(seq(.01, .99, by = .01), function(x) {
      c <- I_spline(x, 3, interior_knots = chosen.xi, individual = T)
      sol <- solveLP(c, b, A,
                     maximum = F,
                     const.dir = constraint_signs,
                     lpSolve = T)
      sol$solution %*% c
    })
  }
  
  ## calculate upper bound
  if (bound %in% c("both", "upper") && nrow(input_upper) != 0) {
    upper_bound <- sapply(seq(.01, .99, by = .01), function(x) {
      c <- I_spline(x, order, interior_knots = chosen.xi, individual = T)
      sol <- solveLP(c, b, A, 
                     maximum = T,
                     const.dir = constraint_signs,
                     lpSolve = T)
      sol$solution %*% c
    })
  }  
  
  if (bound == "lower") return(c(0, lower_bound, 1))
  if (bound == "upper") return(c(0, upper_bound, 1))
  if (bound == "both") return(cbind(
    c(0, lower_bound, 1),
    c(0, upper_bound, 1)))
}




#### Linear regression L1
L1 <- function(lambda) {
  sum(abs(y - X %*% lambda))
}




#### Logistic regression 
negLL <- function(lambda) {
  - sum(s_i * (X %*% lambda) - log(1 + exp(X %*% (lambda))))
}

partial_dnegLL <- function(lambda, ordinal_for_lambda) {
  X[, ordinal_for_lambda] %*% (exp(X %*% (lambda)) / (1 + exp(X %*% (lambda))) - s_i)
}

dnegLL <- function(lambda) {
  sapply(seq(length(lambda)), partial_dnegLL, lambda = lambda)
}




#### Uncontrained logistic regression
negULL <- function(zeta) {
  - sum(s * (X %*% exp(zeta)) - log(1 + exp(X %*% exp(zeta))))
}

partial_dnegULL <- function(zeta, ordinal_for_zeta) {
  (exp(zeta[ordinal_for_zeta]) * X[, ordinal_for_zeta]) %*% (exp(X %*% exp(zeta)) / (1 + exp(X %*% exp(zeta))) - s) 
}

dnegULL <- function(zeta) {
  sapply(1:m, partial_dnegULL, zeta = zeta)
}




##### Significance in difference of mean and median of lambda 
lambda_t.test <- function (which_solutions = "lr_solutions", compare_to = NULL) {
  if(!(which_solutions %in% c("lr_solutions", "logistic_solutions", "svm_solutions")))
    warning("Wrong specification for which solution.")
  
  if (which_solutions == "lr_solutions") solutions_position <- 1
  if (which_solutions == "logistic_solutions") solutions_position <- 8
  if (which_solutions == "svm_solutions") solutions_position <- 7
  
  if (compare_to == "lr_solutions") solutions_position2 <- 1
  if (compare_to == "logistic_solutions") solutions_position2 <- 8
  if (compare_to == "svm_solutions") solutions_position2 <- 7
  
  output <- c()
  for(i in 1:m) {
    input1 <- eval(substitute(sapply(get(a), "[[", b)[c, ],
                              list(a = which_solutions, b = solutions_position, c = i)))
    
    input2 <- eval(substitute(sapply(get(a), "[[", b)[c, ],
                              list(a = compare_to, b = solutions_position2, c = i)))
    temp <- t.test(input1, input2)
    output <- rbind(output,
                    c(abs(diff(temp$estimate))[[1]],
                      temp$p.value))
  }
  return(output)
}




##### Significance in difference of mean and median of lambda 
lambda_mood.test <- function (which_solutions = c("lr_solutions", "logistic_solutions", "svm_solutions"), 
                              compare_to = c("logistic_solutions", "svm_solutions", "lr_solutions")) {
  which_solutions <- match.arg(which_solutions)
  compare_to <- match.arg(compare_to)
  
  if(which_solutions == compare_to)
    warning("You are comparing the same results!")
  
  if (which_solutions == "lr_solutions") solutions_position <- 1
  if (which_solutions == "logistic_solutions") solutions_position <- 8
  if (which_solutions == "svm_solutions") solutions_position <- 7
  
  if (compare_to == "lr_solutions") solutions_position2 <- 1
  if (compare_to == "logistic_solutions") solutions_position2 <- 8
  if (compare_to == "svm_solutions") solutions_position2 <- 7
  
  output <- c()
  for(i in 1:m) {
    input1 <- eval(substitute(sapply(get(a), "[[", b)[c, ],
                              list(a = which_solutions, b = solutions_position, c = i)))
    
    input2 <- eval(substitute(sapply(get(a), "[[", b)[c, ],
                              list(a = compare_to, b = solutions_position2, c = i)))

    overall.median <- median(c(input1, input2))
    input1 <- as.vector(table(input1 < overall.median))
    input2 <- as.vector(table(input2 < overall.median))
    chisq_stat <- sum((input1 - input2)^2 / input2)
    chisq_pvalue <- 1 - pchisq(chisq_stat, df = 3)
    
    output <- c(output,
                chisq_pvalue)
  }
  return(output)
}




#### Calculate the RSS of the fitted I-spline
I_spline_RSS <- function(subject, fit = c("RSS", "RMS")) {
  fit <- match.arg(fit)
  x <- indifference_points[[subject]][[1]]
  y <- indifference_points[[subject]][[3]]
  
  output <- sum((y - I_spline(x, order, chosen.xi, lambda = lr_solutions[[subject]]$solution))^2)
  if (fit == "RMS") 
    output <- sqrt(output/length(x))
  
  return(output)
}




#### Find violated preferences
find.violations <- function(subject = 1:71, pwf = c("all", pwf_list)) {
  pwf <- match.arg(pwf, several.ok = T)
  prediction <- list()
  
  for (i in subject) {
    input1 <- answers[answers$n == i, ]
    x <- input1$p.x
    y <- ifelse(input1$choose.sure == 1, 1, -1)
    temp <- list()
    temp$n <- i
    temp$`p.x` <- x
    temp$pi <- input1$w.p
    
    if ("all" %in% pwf) {
      required_pwf <- pwf_list
    } else {
      required_pwf <- pwf
    }

        for (j in required_pwf) {
      input2 <- individual.results[individual.results$`functional form` == j & individual.results$n == i, ]
      temp[[paste0(j, "_predict")]] <- get(j)(x, input2$r, input2$s)
      temp[[paste0(j, "_above")]] <- input1$w.p - get(j)(x, input2$r, input2$s) < 0
      temp[[j]] <- y * (input1$w.p - get(j)(x, input2$r, input2$s)) < 0
    }
    prediction[[i]] <- temp
  }
  return(prediction)
}




#### kernel for indifference points
Epanechnikov.kernel <- function(x_0, x, bw) {
  sapply(seq(x), function(i) {
    t <- abs(x[i] - x_0) / bw
    if (abs(t) <= 1) {
      3/4 * (1 - t^2)
    } else {
      0
    }
  })
}





Gaussian.kernel <- function(x_0, x, bw) {
  sapply(seq(x), function(i) {
    t <- (x[i] - x_0) / bw
    dnorm(t)
  })
}




kernel.indifference.points <- function(x, y, 
                                       bw = .1, kernel.name = c("Epanechnikov", "Gaussian")) {
  if(length(x) != length(y)) stop("x and y do not have the same length!")
  kernel.name <- match.arg(kernel.name)
  kernel.function.name <- paste0(kernel.name, ".kernel")
  
  output <- sapply(seq(x), function(i) {
    num <- sum(get(kernel.function.name)(x[i], x, bw) * y)
    den <- sum(get(kernel.function.name)(x[i], x, bw))
    output <- num /den
    return(output)
  })
  output <- cbind(x = x, kernel = output)
  output <- output[!duplicated(output), ]
  output <- output[order(output[, 1]), ]
  return(output)
}




knn.indifference.points <- function(x, y,
                                    k = 10, measure = c("median", "mean")) {
  measure <- match.arg(measure)
  if(length(x) != length(y)) stop("x and y do not have the same length!")
  
  output <- sapply(seq(x), function(i) {
    diffs <- abs(x - x[i])
    threshold <- sort(diffs)[k]
    output <- get(measure)(y[diffs <= threshold])
    return(output)
  })
  output <- cbind(x = x, kernel = output)
  output <- output[!duplicated(output), ]
  output <- output[order(output[, 1]), ]
  return(output)
}

