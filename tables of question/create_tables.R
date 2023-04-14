
# load data ---------------------------------------------------------------

library(dplyr)
load('Ready_to_use.Rdata')


# store tables as csv -----------------------------------------------------

for (subject.i in unique(answers$n)) {
  answers %>% 
    filter(n == subject.i) %>% 
    select(outcome.sure, outcome.x, p.x, outcome.y, w.p, choose.sure) -> out
  write.csv(
    out,
    file = paste0('tables of question/answers_', subject.i, '.csv')
  )
}
