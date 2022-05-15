import os
import sys
from collections import defaultdict

args = sys.argv
if len(args) == 2:
    problem = args[1]
else:
    print("usage: python3 temporal_inference_evaluate.py {jsem/plmute}")
    exit(1)

with open(f'{problem}_plain/{problem}_problems_list', 'r') as infile:
    problems = infile.read().splitlines()

score = defaultdict(lambda: [0, 0])
with open(f'./{problem}/overall_results.tsv', 'w') as out:
    out.write('problem_name\tpremise\thypothesis\tpred\tgold\tc/w\tFile exists\n')
    for problem_path in problems:
        _, problem_type, problem_name = problem_path.split('/')
        with open(problem_path, 'r') as infile:
            sentences = infile.read().splitlines()
        with open(f'{problem}_plain/' + problem_type + '/' + problem_name.replace('txt', 'answer'), 'r') as infile:
            gold = infile.read().splitlines()
            gold = gold[0] if gold else ''
        pred_path = f'./{problem}/' + problem_type + '/ja_results/' + problem_name + '.answer'
        negpred_path = f'./{problem}/' + problem_type + '/ja_results/' + \
            problem_name.replace('.txt', '.neg.txt') + '.answer'
        if os.path.exists(pred_path):
            with open(pred_path, 'r') as infile:
                pred = infile.read().splitlines()
                file_exists = (pred != [])
                pred = pred[0] if pred else 'unknown'
            negpred = 'unknown'
            if os.path.exists(negpred_path):
                with open(negpred_path, 'r') as infile:
                    negpred = infile.read().splitlines()
                    file_exists = (negpred != [])
                    negpred = negpred[0] if negpred else 'unknown'
            pred = 'no' if negpred == 'yes' else pred
        else:
            pred = 'unknown'
            file_exists = False
        if gold == pred:
            score[problem_type][0] += 1
        score[problem_type][1] += 1
        out.write(f'{problem_name}\t{"".join(sentences[:-1])}\t{sentences[-1]}\t{pred}\t{gold}\t{pred==gold}\t{file_exists}\n')
    out.write('category_results\n')
    c = 0
    t = 0
    for key in score:
        out.write(f'{key}\t{score[key][0]}/{score[key][1]}\t{score[key][0]/score[key][1]}\n')
        c += score[key][0]
        t += score[key][1]
    out.write(f'overall\t{c}/{t}\t{c/t}\n')
