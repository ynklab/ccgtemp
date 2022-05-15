#!/usr/bin/python3
# -*- coding: utf-8 -*-

import fileinput
import json

def main(args = None):

    rel2label = {'entailment': 'yes', 'contradiction': 'no', 'neutral': 'unknown'}
    for line in fileinput.input():
        data = json.loads(line.strip())
        pair_id = data.get('set', 'train') + '_' + data.get('pairID', '0')
        doc_label = {
            'pair_id': pair_id,
            'set': data.get('set', 'train'),
            'rte_label': rel2label.get(data.get('gold_label', 'neutral'), 'unknown'),
            'sts_label': data.get('similarity', '-1')}
        print(json.dumps(doc_label))


if __name__ == '__main__':
    main()

