#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nltk
from lxml import etree
from xml.etree import ElementTree as ET
import re
from depccg.tools.reader import read_trees_guess_extension
from typing import Tuple, List
from collections import defaultdict
from depccg.tree import Tree
from depccg.cat import Category
from depccg.combinator import guess_combinator_by_triplet, UNKNOWN_COMBINATOR
from depccg.lang import BINARY_RULES
from depccg.tokens import Token
import logging
import argparse


def main():
    parser = argparse.ArgumentParser('')
    parser.add_argument('DIR')
    parser.add_argument('FILE')
    parser.add_argument('PAT')
    args = parser.parse_args()

    xml_file = args.DIR + "/ja_parsed/" + args.FILE + ".jigg.xml"
    txt_file = args.DIR + "/ja_plain/" + args.FILE
    parsed_path = args.DIR + "/ja_parsed/" + args.FILE
    pattern_file = args.PAT
    # jigg.xmlファイルから複合語（名詞が連続している箇所）を特定し，複合語，id，spanの情報の辞書を作成する
    ccgtree = etree.parse(xml_file).getroot()
    sentences = ccgtree[0][0].xpath('sentence')
    with open(txt_file, 'r') as infile:
        sentence_strs = infile.read().splitlines()
    with open(pattern_file, 'r') as infile:
        patterns = infile.read().splitlines()
    patterns = [pattern for pattern in patterns if pattern != '']
    tempex_list = []
    for sentence_str in sentence_strs:
        for pattern in patterns:
            tempexs = list(re.finditer(pattern, sentence_str))
            if tempexs != []:
                tempex_list.append(tempexs)
                break
        else:
            tempex_list.append('')
    tempex_data = {}
    for i, sentence in enumerate(sentences):
        if tempex_list[i] == '':
            continue
        for tempex in tempex_list[i]:
            tempex_surfs = []
            tempex_surf2pos = {}
            position = 0
            midflag = False
            for token in sentence.xpath('.//token'):
                token_attribs = dict(token.attrib)
                if position == tempex.span()[0]:
                    midflag = True
                    tempex_surfs.append(token_attribs['surf'])
                    tempex_surf2pos[token_attribs['surf']] = token_attribs['pos']
                elif position == tempex.span()[1]:
                    midflag = False
                    tmp = " ".join(tempex_surfs)
                    tempex_data[tmp] = {"pos": tempex_surf2pos}
                elif midflag:
                    tempex_surfs.append(token_attribs['surf'])
                    tempex_surf2pos[token_attribs['surf']] = token_attribs['pos']
                position += len(token_attribs['surf'])

    # 複合語ごとにxmlファイルから部分木を取り出しPTBフォーマットにする
    tempex_num = 0
    for k, v in tempex_data.items():
        surf = "".join(k.split())
        with open(parsed_path + ".new" + str(tempex_num) + ".ptb", "w") as f:
            if "以前" in surf or "以降" in surf or "以後" in surf or "以来" in surf:
                if "には" in surf:
                    f.write(
                        f"(S/S (S/S (S/S (NP {surf[:-4]}) (<S/S>\\NP {surf[-4:-2]})) (<S/S>\\<S/S> {surf[-2]})) (<S/S>\\<S/S> {surf[-1]}))")
                else:
                    if "に" in surf or "、" in surf or "は" in surf or ("で" in surf and v["pos"]["で"] == "助詞"):
                        f.write(
                            f"(S/S (S/S (NP {surf[:-3]}) (<S/S>\\NP {surf[-3:-1]})) (<S/S>\\<S/S> {surf[-1]}))")
                    elif "で" in surf and v["pos"]["で"] == "助動詞":
                        f.write(f"(S (NP (NP {surf[:-3]}) (NP\\NP {surf[-3:-1]})) (S\\NP {surf[-1]}))")
                    else:
                        f.write(f"(S/S (NP {surf[:-2]}) (<S/S>\\NP {surf[-2:]}))")
            else:
                if "には" in surf:
                    f.write(f"(S/S (S/S (S/S (NP {surf[:-2]})) (<S/S>\\<S/S> {surf[-2]})) (<S/S>\\<S/S> {surf[-1]}))")
                else:
                    if "に" in surf or "、" in surf or "は" in surf or ("で" in surf and v["pos"]["で"] == "助詞"):
                        f.write(f"(S/S (S/S (NP {surf[:-1]})) (<S/S>\\<S/S> {surf[-1:]}))")
                    elif "で" in surf and v["pos"]["で"] == "助動詞":
                        f.write(f"(S (NP {surf[:-1]}) (S\\NP {surf[-1:]}))")
                    else:
                        f.write(f"(S/S (NP {surf}))")
        tempex_num += 1

    # 置き換え
    with open(parsed_path + ".ptb", 'r') as infile:
        line = infile.read()
    for i in range(tempex_num):
        with open(parsed_path + ".origin" + str(i) + ".ptb", "r") as f:
            origin = f.read()
        with open(parsed_path + ".new" + str(i) + ".ptb", "r") as f:
            new = f.read()
        line = line.replace(origin, new)
    with open(parsed_path + ".mod.ptb", 'w') as outfile:
        outfile.write(line)


if __name__ == '__main__':
    main()
