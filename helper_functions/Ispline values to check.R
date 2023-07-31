source("M-spline and I-spline.R")

I_spline(.1, k = 3, interior_knots = c(.1, .9), individual = TRUE)
I_spline(.5, k = 3, interior_knots = c(.1, .9), individual = TRUE)
I_spline(.8, k = 3, interior_knots = c(.1, .9), individual = TRUE)

I_spline(seq(0, 1, .1), k = 3, interior_knots = c(.1, .9), individual = TRUE)
