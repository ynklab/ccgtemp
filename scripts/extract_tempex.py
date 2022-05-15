#!/usr/bin/python3
# -*- coding: utf-8 -*-

from lxml import etree
import re
from depccg.tree import Tree
from depccg.cat import Category
from depccg.combinator import guess_combinator_by_triplet, UNKNOWN_COMBINATOR
from depccg.lang import BINARY_RULES
from depccg.tokens import Token
import argparse


# jigg.xmlを読み込みパーズするモジュール
def read_jigg_xml_tempex(filename, tempex_ids, tempex_span, lang='ja'):
    binary_rules = BINARY_RULES[lang]

    def try_get_surface(token):
        if 'word' in token:
            return token.word
        elif 'surf' in token:
            return token.surf
        else:
            raise RuntimeError(
                'the attribute for the token\'s surface form is unknown')

    def parse(tree, tokens):
        def rec(node):
            attrib = node.attrib
            if 'terminal' not in attrib:
                cat = Category.parse(attrib['category'])
                children = [rec(spans[child]) for child in attrib['child'].split(' ')]
                if len(children) == 1:
                    return Tree.make_unary(cat, children[0], lang)
                else:
                    assert len(children) == 2
                    left, right = children
                    combinator = guess_combinator_by_triplet(
                        binary_rules, cat, left.cat, right.cat)
                    combinator = combinator or UNKNOWN_COMBINATOR
                    return Tree.make_binary(cat, left, right, combinator, lang)
            else:
                cat = Category.parse(attrib['category'])
                word = try_get_surface(tokens[attrib['terminal']])
                return Tree.make_terminal(word, cat, lang)

        spans = {span.attrib['id']: span for span in tree.xpath('./span')}
        return rec(spans[tree.attrib['root']])

    trees = etree.parse(filename).getroot()
    sentences = trees[0][0].xpath('sentence')
    for i in range(len(sentences)):
        if re.search(f"s{i}", tempex_ids[0]):
            sentences = [sentences[i]]
    for sentence in sentences:
        token_and_ids = []
        for token in sentence.xpath('.//token'):
            token_attribs = dict(token.attrib)
            token_id = token_attribs['id']
            # tempexのtoken情報だけをtoken_and_idsに格納する
            # if token_id not in tempex_ids:
            #    continue
            for no_need in ['id', 'start', 'cat']:
                if no_need in token_attribs:
                    del token_attribs[no_need]
            token_and_ids.append((token_id, Token(**token_attribs)))
        tokens = [token for _, token in token_and_ids]
        # tempexのspanの始点と終点
        sid = tempex_span[0]
        eid = tempex_span[-1]
        # 部分木のrootとなるspan idを新しいrootとする
        newroot = sentence.xpath('./ccg/span[@begin=' + sid + ' and @end=' + eid + ']/@id')
        # print(newroot)

        # sentenceから部分木以外の要素を除く
        for i, ccg in enumerate(sentence.xpath('./ccg')):
            for span in ccg.xpath('./span'):
                if int(span.attrib['begin']) < int(sid) or int(span.attrib['end']) > int(eid):
                    ccg.remove(span)
            # sentence.xpath('./ccg')[i] = ccg

        for ccg in sentence.xpath('./ccg'):
            # rootを新しいrootにセットする
            ccg.set('root', newroot[0])
            tree = parse(ccg, dict(token_and_ids))
            yield ccg.attrib['id'], tokens, tree

# PTBフォーマットに変更するモジュール


def bracket(tree):
    def rec(node):
        if node.is_leaf:
            cat = str(node.cat).replace('(', '<') \
                               .replace(')', '>')
            word = node.word
            return f'({cat} {word})'
        else:
            cat = str(node.cat).replace('(', '<') \
                               .replace(')', '>')
            children = ' '.join(rec(child) for child in node.children)
            return f'({cat} {children})'
    # return f'(ROOT {rec(tree)})'
    return f'{rec(tree)}'


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
            tempex_ids = []
            tempex_span = []
            position = 0
            midflag = False
            for token in sentence.xpath('.//token'):
                token_attribs = dict(token.attrib)
                if position == tempex.span()[0]:
                    midflag = True
                    tempex_span.append(token_attribs['start'])
                    tempex_surfs.append(token_attribs['surf'])
                    tempex_ids.append(token_attribs['id'])
                elif position == tempex.span()[1]:
                    midflag = False
                    tmp = " ".join(tempex_surfs)
                    tempex_span.append(token_attribs['start'])
                    tempex_ids.append(token_attribs['id'])
                    tempex_data[tmp] = {"ids": tempex_ids, "span": tempex_span}
                elif midflag:
                    tempex_span.append(token_attribs['start'])
                    tempex_surfs.append(token_attribs['surf'])
                    tempex_ids.append(token_attribs['id'])
                position += len(token_attribs['surf'])

    # 複合語ごとにxmlファイルから部分木を取り出しPTBフォーマットにする
    tempex_num = 0
    for k, v in tempex_data.items():
        for name, tokens, tree in read_jigg_xml_tempex(xml_file, v['ids'], v['span']):
            # print(bracket(tree))
            # PTBファイルに出力する場合
            with open(parsed_path + ".origin" + str(tempex_num) + ".ptb", "w") as f:
                f.write(bracket(tree))
            with open(args.DIR + "/ja_parsed/" + "tempex.txt", "a") as g:
                g.write(str(tempex_num) + "\t" + k)
                g.write("\n")
            tempex_num += 1
            break


if __name__ == '__main__':
    main()
