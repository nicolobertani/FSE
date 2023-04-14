# General Setup -------------------------------------------------------------------
rm(list = ls())
if (!require(dplyr)) install.packages('dplyr', repos = 'cran.r-project.org', dependencies = T)
library(dplyr)
if (!require(purrr)) install.packages('purrr', repos = 'cran.r-project.org', dependencies = T)
library(purrr)
if (!require(linprog)) install.packages('linprog', repos = 'cran.r-project.org', dependencies = T)
library(linprog)
if (!require(quadprog)) install.packages('quadprog', repos = 'cran.r-project.org', dependencies = T)
library(quadprog)
if (!require(beepr)) install.packages('beepr', repos = 'cran.r-project.org', dependencies = T)

source("helper_functions/Probability weighting functions.R")
source("helper_functions/M-spline and I-spline.R")
source("helper_functions/Helper functions for data analysis.R")
source("helper_functions/graph_helpers.R")
source("helper_functions/run_FSE.R")

load("Ready_to_use.Rdata") ### change to the data produced at the end of final econs
load('viable.Rdata')

defining.fncs <- c(
  "defining.function <- partial(GE, r = .65, s = .6)",
  "defining.function <- partial(GE, r = .84, s = .65)",
  "defining.function <- partial(TK, r = .6)",
  "defining.function <- partial(TK, r = .7)",
  "defining.function <- partial(NeoA, r = 0, s = .52)"
)  

output.location <- "./"

for (function_i in 1:length(defining.fncs)) {
  # function_i <- 1
  
  # Define subject ----------------------------------------------------------
  
  eval(parse(text = defining.fncs[function_i]))
  data <- data.frame(matrix(NA, nrow = 1, ncol = 4))
  colnames(data) <- c('p.x', 'z', 'w.p', 's')
  x <- 120
  y <- 10
  elicited.data <- run.FSE()
  
  data <- elicited.data[[1]]
  data$s <- ifelse(data$s == -1, 0, 1)
  data$s.true <- ifelse(data$s.true == -1, 0, 1)
  data
  
  
  # step-by-step pwf ------------------------------------------------------------
  
  ## Setup ------
  separator <- 9/10
  num_rows <- nrow(data) %/% 2 + 1
  coordinates <- expand.grid(
    list(c(0, 5/21), c(5/21, 10/21), c(11/21, 16/21), c(16/21, 1)), 
    sapply(apply(rbind(
      seq((num_rows - 1) / num_rows * separator, 0, by = -separator / num_rows), 
      seq(separator, separator / num_rows, by = -separator / num_rows)
    ), 2, list), '[', 1)
  )
  coordinates <- matrix(apply(coordinates, 1, unlist), ncol = 4, byrow = T)
  
  
  ## Create frame and legend ----
  {
    png(paste0(output.location, "illustration_of_procedure-", function_i, ".png"),
        width = 800 * 1.5, height = 1250 * 1.5, pointsize = 18) # size for one full page
    
    ### add legend
    par(fig = c(0, 1, separator, 1), new = F,
        mar = c(0,0,0,0), oma = c(0,0,0,0), xpd = T)
    plot(0:1, 0:1, type = 'n', axes = F, xlab = NA, ylab = NA)
    
    legend(x = -.04, y = 1,
           legend = c("Basic elements:", "True pwf", "Diagonal"),
           lty = c(NA, 1, 2),
           lwd = c(NA, 2.5, 1),
           col = c(NA, cols[3], gray(.5)),
           text.font = c(1, 3, 3),
           cex = 1, box.lty = "blank", y.intersp = 1.2, seg.len = 1.5
    )
    
    legend(x = .14, y = 1,
           legend = c('Inadmissible area:', "Chose sure", "Chose lottery"),
           fill = c(NA, cols[2:1]),
           border = NA,
           text.font = c(1, 3, 3),
           cex = 1, box.lty = "blank", y.intersp = 1.2
    )
    
    legend(x = .35, y = 1,
           legend = c("Questions:", "Chose sure", "Chose lottery", 'Next question', 'Response error'),
           pch = c(NA, 19, 19, 19, 4),
           col = c(NA, cols[2:1], gray(.5), gray(.5)),
           pt.lwd = c(NA, 1, 1, 1, 4),
           text.font = c(1, 3, 3, 3, 3),
           cex = 1, box.lty = "blank", y.intersp = 1.2
    )
    
    legend(x = .50, y = 1,
           legend = c("Bounds (functional space):", "Upper", "Lower"),
           lty = c(1, 1),
           lwd = c(2, 2),
           col = c(NA, cols[2:1]),
           text.font = c(1, 3, 3),
           cex = 1, box.lty = "blank", y.intersp = 1.2, seg.len = 1.5
    )
    
    legend(x = .75, y = 1,
           legend = c("Constraints (parametric space):", "Chose sure", "Chose lottery"),
           lty = c(1, 1),
           lwd = c(2, 2),
           col = c(NA, ggplot2::alpha(cols[2:1], .8)),
           text.font = c(1, 3, 3),
           cex = 1, box.lty = "blank", y.intersp = 1.2, seg.len = 1.5
    )
    
    
    ### create empty plot to reset graphical parameters - suboptimal
    par(fig = coordinates[1,], new = T, mar = c(0, 0, 2, 0), oma = c(2.7, .5, 0, 0), xaxs = "i", yaxs = "i", pty = "s")
    plot(0:1, 0:1, type = 'n', axes = F, xlab = NA, ylab = NA)
    
    ## create labels for the step
    step.number <- c(
      'Step 0 - start',
      paste('Step', 1:(nrow(elicited.data[[1]]) - 1), sep = ' '),
      paste('Step', nrow(elicited.data[[1]]), '- stop', sep = ' ')
    )
    
    ### create helpers, storage
    helper <- seq(0, 1, .01)
    A1 <- matrix(rep(rep(0, m), m), ncol = m)
    diag(A1) <- 1
    hyperplanes <- matrix(NA, ncol = 5, nrow = nrow(data))
    colnames(hyperplanes) <- c('int.m', 'slope', 'p.x', 'p.y', 'int.1')
    
    
    ## Create step graphs ------
    
    for (i in 0:nrow(data)) {
      # i <- 10
      
      ### select data
      input <- head(data, i)
      next.q <- tail(head(data, i+1), 1)
      
      ### pwp graph -----
      par(fig = coordinates[i %% num_rows * 4 + 1 + (i %/% num_rows) * 2, ], 
          new = T, xaxs = "i", yaxs = "i", pty = "s")
      # par(fig = coordinates[(i + 1) * 2 - 1, ], new = T, xaxs = "i", yaxs = "i", pty = "s")
      # par(mfrow = c(1,2))
      
      # frame
      s(xaxt = 'n', yaxt = 'n')
      # add true pwf
      curve(defining.function(x), 0, 1, 
            col = cols[3], add = T, lwd = 2.5)
      
      ## add axes and labels
      # generic x-axis
      axis(1, 
           at = seq(0, 1, .2), 
           label = F, 
           tick = T, tcl = -.3)
      # generic y-axis
      axis(2, 
           at = seq(0, 1, .2), 
           label = F,
           tick = T, tcl = -.3)
      axis(2, 
           at = seq(0, 1, .2), 
           label = c('0', '.2', '.4', '.6', '.8', '1'), line = -.6, 
           tick = F, cex.axis = .8)
      # y-axis label
      mtext("w(p)",
            side = 2, line = 1.6, outer = F, cex = 1.2, font = 4)
      # add text with step number
      mtext(step.number[i + 1],
            side = 3, line = .2, outer = F, cex = 1, font = 2, adj = 0)
      # top graphs
      if (i %% num_rows == 0) {
        mtext("functional space",
              side = 3, line = 2, outer = F, cex = 1.3, font = 2)
      }
      # bottom graphs
      if (i %% num_rows == (num_rows - 1) || i == nrow(data) + 1) {
        axis(1, 
             at = seq(0, 1, .2), 
             label = c('0', '.2', '.4', '.6', '.8', '1'), line = -.6,
             tick = F, cex.axis = .8)
        mtext("p",
              side = 1, line = 1.6, outer = F, cex = 1.2, font = 4)
      }
      
      ## add previous questions - points
      with(input,
           points(w.p ~ p.x,
                  xlim = c(0,1), ylim = c(0,1),
                  col = cols[1 + s],
                  pch = ifelse(correct, 16, 4),
                  lwd = ifelse(correct, 1, 4)
           ))
      
      ## add previous questions - areas and segments
      for (j in seq(nrow(input))) {
        with(input[j, ],
             {
               polygon(x = c(p.x, p.x, !s, !s),
                       y = c(s, w.p, w.p, s),
                       border = NA,
                       col = ggplot2::alpha(cols[s + 1], .1))
               segments(x0 = p.x, y0 = s,
                        x1 = p.x, y1 = w.p,
                        col = ggplot2::alpha(cols[s + 1], .3),
                        lwd = 1, lty = 2)
               segments(x0 = p.x, y0 = w.p,
                        x1 = !s, y1 = w.p,
                        col = ggplot2::alpha(cols[s + 1], .3),
                        lwd = 1, lty = 1)
             }
        )
      }
      
      ## add bounds
      polygon(x = c(1, helper),
              y = c(0, elicited.data[[4]][[i + 1]]['lower_bound', ]), 
              border = NA, col = ggplot2::alpha(cols[1], .2))
      polygon(x = c(0, helper),
              y = c(1, elicited.data[[4]][[i + 1]]['upper_bound', ]), 
              border = NA, col = ggplot2::alpha(cols[2], .2))
      
      points(helper, elicited.data[[4]][[i + 1]]['lower_bound', ], type = 'l', 
             col = ggplot2::alpha(cols[1], .8), lwd = 2, lty = 1)
      points(helper, elicited.data[[4]][[i + 1]]['upper_bound', ], type = 'l', 
             col = ggplot2::alpha(cols[2], .8), lwd = 2, lty = 1)
      
      ## next question
      if(i == nrow(data)) {
        D <- elicited.data[[4]][[i + 1]]['upper_bound', ] - elicited.data[[4]][[i + 1]]['lower_bound', ]
        new.x <- if (sum(D == max(D)) == 1) {
          helper[which.max(D)]
        } else {
          helper[which.max(D)][which.max(abs(helper[which.max(D)] - .5))]
        } 
        new.w.p <- ((elicited.data[[4]][[i + 1]]['upper_bound', ] + elicited.data[[4]][[i + 1]]['lower_bound', ])[which.max(D)] / 2)[1]
        points(new.x, new.w.p, col = gray(.5), pch = 19)
      } else {
        points(next.q$p.x, next.q$w.p, col = gray(.5), pch = 16)
      }
      
      
      ## simplex graph -----
      par(fig = coordinates[i %% num_rows * 4 + 2 + (i %/% num_rows) * 2, ],
          new = T, xaxs = "i", yaxs = "i", pty = "s")
      # par(fig = coordinates[(i + 1) * 2, ], new = T, xaxs = "i", yaxs = "i", pty = "s")
      
      simplex()      
      # generic x-axis
      axis(1, at = c(0, 1), labels = F, 
           tick = T, tcl = -.3)
      # generic y-axis
      axis(2, at = c(0, 1), labels = F, 
           tick = T, tcl = -.3)
      axis(2, at = c(0, 1), labels = T, line = -.6, 
           tick = F, cex.axis = .8)
      mtext(expression(lambda[5]), 
            side = 2, line = .5, outer = F, cex = 1.3, font = 1)
      text(.57, .57, expression(lambda[2] + lambda[3] + lambda[4]), cex = 1.3, font = 2, srt = -45)
      # bottom graph
      if (i %% num_rows == (num_rows - 1) || i == nrow(data) + 1) {
        axis(1, at = c(0, 1), labels = T, line = -.6,
             tick = F, cex.axis = .8)
        mtext(expression(lambda[1]), side = 1, line = 1.6, cex = 1.3, font = 2)
      }
      # top graph
      if (i %% num_rows == 0) {
        mtext("parametric space",
              side = 3, line = 2, outer = F, cex = 1.3, font = 2)
      }
      
      if (i <= nrow(elicited.data[[1]])) {
        if (i > 0) {
          I_s.i <- I_spline(data$p.x[i], order, interior_knots = chosen.xi, individual = T)
          
          # for lambda 1
          l1.intercepts.bool <- sapply(seq(nrow(viable)), function (ii) {
            I_s.i[1] %*% viable[ii, ][1] >= data$w.p[i] - I_s.i[-1] %*% c(viable[ii, ], 0)[-1]
          })
          
          # for lambda m
          lm.intercepts.bool <- sapply(seq(nrow(viable)), function (ii) {
            I_s.i[m] %*% viable[ii, ][m - 1] >= data$w.p[i] - I_s.i[-m] %*% c(0, viable[ii, ])[-m]
          })
          
          # for other lambdas all 0
          l.other.bool <-
            cbind(seq(0, 1, by =.01), 0, 0, 0, seq(1, 0, by = -.01)) %*%
            I_spline(data$p.x[i], order, interior_knots = chosen.xi, individual = T) >= data$w.p[i]
          
          if (data$s[i]) {
            intercept.m <- ifelse(length(viable[!lm.intercepts.bool, m - 1]), 
                                  min(viable[!lm.intercepts.bool, m - 1]), 
                                  1)
            intercept.1 <- ifelse(length(viable[!l1.intercepts.bool, 1]), 
                                  max(viable[!l1.intercepts.bool, 1]),
                                  0)
            l.other.point <- tail(
              cbind(seq(0, 1, by =.01), 0, 0, 0, seq(1, 0, by = -.01))[!l.other.bool, c(1, m)],
              1)
          } else {
            intercept.m <- ifelse(length(viable[lm.intercepts.bool, m - 1]), max(viable[lm.intercepts.bool, m - 1]), 1)
            intercept.1 <- ifelse(length(viable[l1.intercepts.bool, 1]), min(viable[l1.intercepts.bool, 1]), 1)
            l.other.point <- head(cbind(seq(0, 1, by =.01), 0, 0, 0, seq(1, 0, by = -.01))[l.other.bool, c(1, m)], 1)
          }
          
          hyperplanes[i, ] <- c(intercept.m, NA, l.other.point, intercept.1)
          for (hp.i in which(apply(!is.na(hyperplanes), 1, any))) {
            segments(hyperplanes[hp.i, 5],
                     ifelse(hyperplanes[hp.i, 1] == 1, 0, hyperplanes[hp.i, 1]),
                     hyperplanes[hp.i, 3],
                     hyperplanes[hp.i, 4],
                     col = ggplot2::alpha(cols[data$s[hp.i] + 1], .8), lwd = 1, lty = 1)
            polygon(
              x = c(
                hyperplanes[hp.i, 5], 
                hyperplanes[hp.i, 3], 
                data$s[hp.i], 
                0),
              y = c(
                ifelse(hyperplanes[hp.i, 1] == 1, 0, hyperplanes[hp.i, 1]),
                hyperplanes[hp.i, 4],
                !data$s[hp.i],
                ifelse(hyperplanes[hp.i, 1] == 1, 0, !data$s[hp.i])), 
              border = NA, col = ggplot2::alpha(cols[data$s[hp.i] + 1], .1))
          }
        }
      }
    }
    
    dev.off()
    beepr::beep(2)
  }
  
  
  ## p/wp graph --------------------------------------------------------------
  
  axis.label.size <- 1.2
  axis.label.spacing <- -.2
  
  png(paste0(output.location, "illustration_of_procedure-", function_i, "-fs.png"),
      width = 600, height = 600, pointsize = 18)
  single_graph_par()
  
  # frame
  empty_s()
  add_axes()
  add_ax_labels()
  
  
  ## add previous questions - points
  with(data,
       points(w.p ~ p.x,
              xlim = c(0,1), ylim = c(0,1),
              col = cols[1 + s],
              pch = ifelse(correct, 16, 4),
              lwd = ifelse(correct, 1, 4)
       ))
  
  ## add previous questions - areas and segments
  for (j in seq(nrow(data))) {
    with(data[j, ],
         {
           polygon(x = c(p.x, p.x, !s, !s),
                   y = c(s, w.p, w.p, s),
                   border = NA,
                   col = ggplot2::alpha(cols[s + 1], .1))
           segments(x0 = p.x, y0 = s,
                    x1 = p.x, y1 = w.p,
                    col = ggplot2::alpha(cols[s + 1], .3),
                    lwd = 1, lty = 2)
           segments(x0 = p.x, y0 = w.p,
                    x1 = !s, y1 = w.p,
                    col = ggplot2::alpha(cols[s + 1], .3),
                    lwd = 1, lty = 1)
         }
    )
  }
  
  ## add bounds
  polygon(x = c(1, helper),
          y = c(0, tail(elicited.data[[4]], 1)[[1]]['lower_bound', ]),
          border = NA, col = ggplot2::alpha(cols[1], .2))
  polygon(x = c(0, helper),
          y = c(1, tail(elicited.data[[4]], 1)[[1]]['upper_bound', ]),
          border = NA, col = ggplot2::alpha(cols[2], .2))
  
  points(helper, tail(elicited.data[[4]], 1)[[1]]['lower_bound', ], type = 'l',
         col = ggplot2::alpha(cols[1], .8), lwd = 2, lty = 1)
  points(helper, tail(elicited.data[[4]], 1)[[1]]['upper_bound', ], type = 'l',
         col = ggplot2::alpha(cols[2], .8), lwd = 2, lty = 1)
  
  # add true pwf
  curve(defining.function(x), 0, 1,
        col = cols[3], add = T, lwd = 3)
  # add true pwf
  curve(defining.function(x), 0, 1,
        col = cols[3], add = T, lwd = 3)
  # add fits
  curve(I_spline(x, order, chosen.xi, lambdas = elicited.data[[3]]$normalized_solution),
        xlim = c(0, 1), lwd = 3, lty = 1, add = T)
  
  legend('topleft',
         lty = 1, lwd = 3,
         legend = "functional estimate",
         seg.len = 1.5,
         cex = 1.2, box.col = 'transparent', bg = ggplot2::alpha('white', .95)
  )
  
  dev.off()
  
  
  ## simplex graph ------
  
  png(paste0(output.location, "illustration_of_procedure-", function_i, "-ps.png"),
      width = 600, height = 600, pointsize = 18)
  single_graph_par()
  
  simplex()
  simplex.axes()
  text(.55, .55, expression(lambda[2] + lambda[3] + lambda[4]), cex = 1.4, font = 2, srt = -45)
  mtext(expression(lambda[5]), side = 2, line = 1.9, cex = 1.4, font = 1)
  mtext(expression(lambda[1]), side = 1, line = 2.1, cex = 1.4, font = 2)
  mtext("parametric space",
        side = 3, line = 1, outer = F, cex = 1.3, font = 2)
  
  for (hp.i in which(apply(!is.na(hyperplanes), 1, any))) {
    segments(hyperplanes[hp.i, 5],
             ifelse(hyperplanes[hp.i, 1] == 1, 0, hyperplanes[hp.i, 1]),
             hyperplanes[hp.i, 3],
             hyperplanes[hp.i, 4],
             col = ggplot2::alpha(cols[data$s[hp.i] + 1], .8), lwd = 1, lty = 1)
    polygon(
      x = c(
        hyperplanes[hp.i, 5],
        hyperplanes[hp.i, 3],
        data$s[hp.i],
        0),
      y = c(
        ifelse(hyperplanes[hp.i, 1] == 1, 0, hyperplanes[hp.i, 1]),
        hyperplanes[hp.i, 4],
        !data$s[hp.i],
        ifelse(hyperplanes[hp.i, 1] == 1, 0, !data$s[hp.i])),
      border = NA, col = ggplot2::alpha(cols[data$s[hp.i] + 1], .1))
  }
  
  points(elicited.data[[3]]$normalized_solution[1],
         elicited.data[[3]]$normalized_solution[m],
         pch = 21,
         bg =  ggplot2::alpha(1, .25),
         col = ggplot2::alpha(1, 1),
         lwd = 2
  )
  legend('topright',
         legend = c('parameter estimates'),
         pch = 21, pt.lwd = 2,
         pt.bg =  ggplot2::alpha(1, .25),
         col = ggplot2::alpha(1, 1),         
         cex = 1.2, box.col = 'transparent', bg = ggplot2::alpha('white', .95)
  )
  
  
  dev.off()
  
  
  ## difference bw bounds -----
  
  png(paste0(output.location, "illustration_of_procedure-", function_i, "-db.png"),
      width = 600, height = 600, pointsize = 18)
  single_graph_par()
  par(xpd = F, mar = c(2.7, 3.1, 0, 0))
  
  plot(helper, elicited.data[[2]][2, ] - elicited.data[[2]][1, ],
       type = 'l', lwd = 3, col = "deepskyblue3",
       ylim = c(0, .1), xaxt = 'n', yaxt = 'n',
       xlab = NA, ylab = NA)
  # abline(h = mean(elicited.data[[2]][2, ] - elicited.data[[2]][1, ]), lty = 2, lwd = 2, col = "deepskyblue3")
  
  ## add axes and labels
  axis(1,
       at = seq(0, 1, .2),
       label = F,
       tick = T, tcl = -.3)
  axis(1,
       at = seq(0, 1, .2),
       label = c('0', '.2', '.4', '.6', '.8', '1'), line = axis.label.spacing,
       tick = F, cex.axis = axis.label.size)
  # generic y-axis
  axis(2,
       at = seq(0, .13, .02),
       label = F,
       tick = T, tcl = -.3)
  axis(2,
       at = seq(0, .13, .02),
       label = c('0', '.02', '.04', '.06', '.08', '.1', '.12'), line = axis.label.spacing,
       tick = F, cex.axis = axis.label.size)
  # labels
  mtext('absolute distance',
        side = 2, line = 2.1, outer = F, cex = 1.4, font = 1)
  mtext("p",
        side = 1, line = 2.0, outer = F, cex = 1.2, font = 4)
  mtext('distance at termination',
        side = 3, line = 1, outer = F, cex = 1.3, font = 2)
  
  # add distance lines
  abline(h = mean(elicited.data[[2]]['upper_bound', ] - elicited.data[[2]]['lower_bound', ]),
         lty = 2, lwd = 2, col = "deepskyblue3")
  d2true <- abs(
    I_spline(helper, order, chosen.xi, lambdas = elicited.data[[3]]$normalized_solution) - defining.function(helper)
  )
  lines(helper, d2true, lwd = 3, col = "magenta2")
  abline(h = mean(d2true), lty = 2, lwd = 2, col = "magenta2")
  
  # add legend
  legend(
    "topleft",
    legend = c("between bounds", "   average", "fit to truth", "   average"),
    col = c("deepskyblue3", "deepskyblue3", 'magenta2', 'magenta2'),
    lty = c(1, 2), lwd = c(3, 2),
    seg.len = 1.5, bty = "n", cex = 1.2
  )
  
  dev.off()
  
}
