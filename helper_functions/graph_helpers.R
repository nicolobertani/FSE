
# generic -----------------------------------------------------------------

helper <- seq(0, 1, .01)

cols <- c(
  rgb(.8,0,0),
  rgb(26/255,48/255,132/255),
  rgb(0,.6,0))

cols2 <- c('steelblue',
           'orange',
           'springgreen4'
)

cols2 <- c(
  'darkred',
  'steelblue',
  'orange',
  'springgreen4',
  'pink2'
)

cols3 <- c(
  'deepskyblue',
  'violet',
  'chartreuse3',
  'tomato'
)

cols4 <- c(
  'skyblue',
  'hotpink',
  'limegreen',
  'navy'
)


# single graphs -----------------------------------------------------------

single_graph_par <- function(...) {
  par(mfrow = c(1, 1), xpd = T, mar = c(2.7, 3.1, 0, 0), oma = c(0, 0, 0, .1) + .1, xaxs = "i", yaxs = "i", pty = "s")
}

add_axes <- function(axis.label.size = 1.2,
                     axis.label.spacing = -.2
) {
  ## x-axis
  axis(1,
       at = seq(0, 1, .2),
       label = F,
       tick = T, tcl = -.3)
  axis(1,
       at = seq(0, 1, .2),
       label = c('0', '.2', '.4', '.6', '.8', '1'), line = axis.label.spacing,
       tick = F, cex.axis = axis.label.size)
  # y-axis
  axis(2,
       at = seq(0, 1, .2),
       label = F,
       tick = T, tcl = -.3)
  axis(2,
       at = seq(0, 1, .2),
       label = c('0', '.2', '.4', '.6', '.8', '1'), line = axis.label.spacing,
       tick = F, cex.axis = axis.label.size)
}

add_ax_labels <- function(...) {
  mtext("p",
        side = 1, line = 2.0, outer = F, cex = 1.2, font = 4)
  mtext("w(p)",
        side = 2, line = 2.2, outer = F, cex = 1.2, font = 4)
}

empty_s <- function() {
  s(xaxt = 'n', yaxt = 'n')
}


# simplex graph -----------------------------------------------------------

simplex <- function() {
  plot(c(0,1), c(0,1),
       type = "n",
       axes = F,
       xlab = NA,
       ylab = NA,
       ylim = c(0,1),
       xlim = c(0,1),
       cex.axis = .8,
       cex.lab = .9)
  segments(0, 1, 1, 0)  
}  

simplex.axes <- function(axis.label.size = 1.2,
                         axis.label.spacing = -.2
) {
  axis(1, at = c(0, 1), labels = F,
       tick = T, tcl = -.3)
  axis(1, at = c(0, 1), labels = T, line = axis.label.spacing,
       tick = F, cex.axis = axis.label.size)
  axis(2, at = c(0, 1), labels = F,
       tick = T, tcl = -.3)
  axis(2, at = c(0, 1), labels = T, line = axis.label.spacing,
       tick = F, cex.axis = axis.label.size)
}
