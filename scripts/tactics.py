# -*- coding: utf-8 -*-

def get_tactics():
    tactics = 'Set Firstorder Depth 1. nltac. Set Firstorder Depth 6. nltac. Qed'
    try:
        with open('tactics_coq.txt') as fin:
            tactics = fin.read().strip()
    except:
        pass
    return tactics

