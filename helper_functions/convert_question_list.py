import rpy2.robjects as robjects
import numpy as np
import json

# Load the RData file
robjects.r['load']("backend/Bayesian_sequence.Rdata")

# convert the question list to a python dictionary
question_list_py = {}
for ii in range(len(robjects.r['question.list'])):

    if ii > 0:
        ii_entries = []
        for jj in range(len(robjects.r['question.list'][ii])):
            entry = {
                'Q' : str(int(robjects.r['question.list'][ii][jj][0].rx2('Q')[0])) + '.' + str(jj+1),
                'p_x' : np.array(robjects.r['question.list'][ii][jj][0].rx2('px')),
                'w_p' : np.array(robjects.r['question.list'][ii][jj][0].rx2('wp')),
                's' : np.array(robjects.r['question.list'][ii][jj][0].rx2('s'))[:-1],
            }
            ii_entries.append(entry)
        question_list_py.update({ii : ii_entries})


# print(question_list_py)
# print([len(q) for q in question_list_py.values()])
# print([np.log2(len(q)) for q in question_list_py.values()])

# save the question list to a json file
with open('backend/question_list.json', 'w') as json_file:
    json.dump(question_list_py, json_file, indent=4, default=lambda x: x.tolist() if isinstance(x, np.ndarray) else x)
