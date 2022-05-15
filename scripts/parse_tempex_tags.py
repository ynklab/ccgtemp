#!/usr/bin/python3
# -*- coding: utf-8 -*-
import nltk
from lxml import etree
from xml.etree import ElementTree as ET
import re
import argparse

#CFG規則の読み込み
grammar1 = nltk.CFG.fromstring("""
  NP_tempex -> NP_wo NP_wo/NP_ev | NP_ga NP_ga/NP_ev
  NP_wo/NP_ev -> "EV"
  NP_ga/NP_ev -> "EV"
  NP_wo -> "WO" | PP_1 "WO" 
  NP_ga -> "GA" | PP_1 "GA" 
  PP_1 -> "PP" | PP_2 "PP" | "M_EN" | "POS"
  PP_2 -> "PP"
  """)

#読み込んだCFG規則に基づいて予測した複合語タグをパーズする
finidx = 0
def traverse(tree, tempex, tempex_surf):
    global finidx
    for index, subtree in enumerate(tree):
        idx = []
        if type(subtree) == nltk.tree.Tree:
            traverse(subtree, tempex, tempex_surf)
        elif type(subtree) == str:
            idx = [i for i, x in enumerate(tempex) if x == subtree and i >= finidx]
            subtree = tempex_surf[idx[0]]
            finidx += 1
            tree[index] = subtree
            

def main():
    parser = argparse.ArgumentParser('')
    #parser.add_argument('FILE')
    parser.add_argument("--surf", nargs='?', type=str, help="tempex surface")
    parser.add_argument("--tags", nargs='?', type=str, help="tempex tags")
    args = parser.parse_args()
    #tempex_surf = "嚥下　困難　出現".split()
    #tempex = "M_EN GA EV".split()
    surf = args.surf
    tags = args.tags
    tempex_surf = surf.split()
    tempex = tags.split()

    rd_parser = nltk.RecursiveDescentParser(grammar1)
    for tree in rd_parser.parse(tempex):
        traverse(tree, tempex, tempex_surf)
        #print(tree.leaves())
        #PTBファイルに出力
        with open("tempex_new.ptb", "w") as f:
            f.write(str(tree))

if __name__ == '__main__':
    main()