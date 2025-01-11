import rpy2.robjects as robjects
import numpy as np

# Activate the automatic conversion of R objects to pandas objects
# from rpy2.robjects import pandas2ri
# pandas2ri.activate()

# Load the RData file
robjects.r['load']("~/elicit/code/Bayesian_FSE/noisy_simulation/noisy_simulation-results/LR_luce_gamma-question_list-2_18-20250101-complete.Rdata")

# Extract the question list
question_list = robjects.r['question.list']

def sequence_next_q(answer_vec=None):
    if answer_vec is None:
        answer_vec = []

    if len(answer_vec) == 0:
        next_q_list = question_list[len(answer_vec) + 1]
        next_q = next_q_list[0][0]

    elif len(answer_vec) == 1:
        answer_sequences = [
            q.rx2('s')[0] for q_sublist in question_list[len(answer_vec)] for q in q_sublist
        ]
        which_answer_seq = np.where(np.array(answer_sequences) == answer_vec[0])[0]
        next_q_list = question_list[len(answer_vec) + 1]
        next_q = next_q_list[int(which_answer_seq[0])][0]

    else:
        answer_sequences = [
            q.rx2('s') for q_sublist in question_list[len(answer_vec)] for q in q_sublist
        ]
        which_answer_seq = np.where([np.all(answer_seq == np.array(answer_vec)) for answer_seq in answer_sequences])[0]
        next_q_list = question_list[len(answer_vec) + 1]
        next_q = next_q_list[int(which_answer_seq[0])][0]

    return next_q

# Example usage
# print(sequence_next_q())
# print(sequence_next_q([0]))
# print(sequence_next_q([1]))
print(sequence_next_q([0,1]))
print(sequence_next_q([0, 1, 1]))
