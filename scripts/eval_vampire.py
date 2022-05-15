# -*- coding: utf-8 -*-

import argparse
from ntpath import join
from lxml import etree
from more_itertools import first
from nltk import *
from nltk.sem import Expression
from nltk.sem.logic import *
import os
import subprocess
import sys
import textwrap
import time
from collections import defaultdict
from multiprocessing import Queue, Process
import re
# from abduction_event import get_axioms # WordNet公理補完（Vampireバージョン）
from linguistic_tools import is_antonym
from os.path import expanduser
from nltk2tptp import convert_to_tptp_proof, convert_to_tptp
from nltk2normal import get_atomic_formulas, rename_variable
lexpr = Expression.fromstring

HOME = expanduser("~")
file = open("./vampire_location.txt")
vampire_dir = file.read().strip()
sys.path.append("./scripts")

# types of predicates
non_Sub = ['former', 'true', 'false']
clause = ['before']
datasets = ['med', 'hans']


# TODO: 英語なのとccgcompの公理のまま。品詞ごと・特定のパターンで公理を作成する関数？
# def vampire_axioms(adjdic, antonyms, Objs, tVerbs, iVerbs, predicates, lst):
#     axiom = []
#     types = []

#     for pred in predicates:
#         # print(pred)
#         if pred[0][0] == '_':
#             pred[0] = pred[0][1:]

#         if (pred[0] == 'many') and not (pred[0] in adjdic):
#             adjdic[pred[0]] = 'POS'
#         if (pred[0] == 'few') and not (pred[0] in adjdic):
#             adjdic[pred[0]] = 'NEG'

#         if '$less' in pred[0]:
#             deg = lexpr('$less(0,_d0)')
#             axiom.append(deg)
#             many_type = 'tff(many_type, type , many : $i * $int > $o).'
#             types.append(many_type)
#             ax1 = lexpr('all x d1. (many(x,d1) -> all d2. ($lesseq(d2,d1) -> many(x,d2)))')
#             axiom.append(ax1)

#         # Adjectives
#         if pred[0] in adjdic:
#             if '_d0' in pred[1][1]:
#                 deg = lexpr('$less(0,_d0)')
#                 axiom.append(deg)
#             if 'person' in Objs:
#                 if '_np' in pred[1][1]:
#                     defcom = lexpr('all x. (' + pred[0] +
#                                    '(x,_np(_u,_th(_u))) <-> ' + pred[0] +
#                                    '(x,_np(_person,_th(_person))))')
#                 else:
#                     defcom = lexpr('all x. (' + pred[0] + '(x,_th(_u)) \
#                     <-> ' + pred[0] + '(x,_th(_person)))')
#                 axiom.append(defcom)

#             if '_np' in pred[1][1]:
#                 np = lexpr('all x d1 d2.($lesseq(d1,d2) <-> $lesseq(_np(x,d1),_np(x,d2)))')
#                 axiom.append(np)

#             # Positive adjectives
#             if antonyms != [] or '_th(' not in ((pred[1])[1]):
#                 if adjdic[pred[0]][:3] == 'POS':
#                     if '$' in pred[1][1]:
#                         upper = lexpr('all x. exists d1.(' + pred[0] +
#                                       '(x,d1) & -exists d2.($less(d1,d2) & ' +
#                                       pred[0] + '(x,d2)))')
#                         axiom.append(upper)
#                     if pred[0] != 'many' or (pred[1][1])[0] != 'd':
#                         ax1 = lexpr('all x d1. (' + pred[0] +
#                                     '(x,d1) -> all d2. ($lesseq(d2,d1) -> '
#                                     + pred[0] + '(x,d2)))')
#                         axiom.append(ax1)

#             # Negative adjectives
#                 elif adjdic[pred[0]][:3] == 'NEG':
#                     if '$' in pred[1][1]:
#                         lower = lexpr('all x. exists d1.(' + pred[0] +
#                                       '(x,d1) & -exists d2.($less(d2,d1) & '
#                                       + pred[0] + '(x,d2)))')
#                         axiom.append(lower)

#                     if pred[0] != 'few' or (pred[1][1])[0] != 'd':
#                         ax2 = lexpr('all x d1. (' + pred[0] +
#                                     '(x,d1) -> all d2. ($lesseq(d1,d2) -> '
#                                     + pred[0] + '(x,d2)))')
#                         axiom.append(ax2)
#                 else:
#                     pass

#         elif pred[0] == 'AccI':
#             att1 = lexpr('all e. (AccI(e,' + pred[1][1] +
#                          ') -> (_know(e) ->' + pred[1][1] + '))')
#             att2 = lexpr('all e. (AccI(e,' + pred[1][1] +
#                          ') -> (_forget(e) ->' + pred[1][1] + '))')
#             att3 = lexpr('all e. (AccI(e,' + pred[1][1] +
#                          ') -> (_learn(e) ->' + pred[1][1] + '))')
#             att4 = lexpr('all e. (AccI(e,' + pred[1][1]
#                          + ') -> (_remember(e) ->' + pred[1][1] + '))')
#             att5 = lexpr('all e. (AccI(e,' + pred[1][1] +
#                          ') -> (_manage(e) ->' + pred[1][1] + '))')
#             att6 = lexpr('all e. (AccI(e,' + pred[1][1] +
#                          ') -> (_fail(e) -> -' + pred[1][1] + '))')
#             axiom.extend([att1, att2, att3, att4, att5, att6])

#         # former
#         elif (('former' in pred[0]) and (type(pred[1][0]) is str)):
#             aff = lexpr('all x. (_former(' + pred[1][0] +
#                         ') -> -' + pred[1][0] + ')')
#             axiom.append(aff)

#         elif pred[0] == 'true':
#             tr = lexpr('_true(' + pred[1][0] + ') -> ' + pred[1][0])
#             axiom.append(tr)

#         elif pred[0] == 'false':
#             fl = lexpr('_false(' + pred[1][0] + ') -> -' + pred[1][0])
#             axiom.append(fl)

#         else:
#             pass

#     if antonyms != []:
#         for antonym in antonyms:
#             Fp = antonym[0]
#             Fm = antonym[1]
#             ax3 = lexpr('all x d.(' + Fp + '(x,d) <-> -' + Fm + '(x,d))')
#             axiom.append(ax3)

#     if lst != []:
#         for i in range(len(Objs)):
#             for j in range(len(Objs)):
#                 if not Objs[i] == Objs[j]:
#                     ax = lexpr('(all x. (' + Objs[i] +
#                                '(x) <-> ' + Objs[j] +
#                                '(x))) <-> (_th(' + Objs[i] + ') = _th('
#                                + Objs[j] + '))')
#                     axiom.append(ax)

#     if tVerbs != []:
#         for verb in tVerbs:
#             verbax = lexpr('all e1 e2.(' + verb + '(e1) & ' + verb + '(e2)  & (subj(e1) = subj(e2)) & (acc(e1) = acc(e2)) -> (e1 = e2))')
#             if verbax not in axiom:
#                 axiom.append(verbax)
#     if iVerbs != []:
#         for verb in iVerbs:
#             verbax = lexpr('all e1 e2.(' + verb + '(e1) & ' + verb +
#                            '(e2) & (subj(e1) = subj(e2)) -> (e1 = e2))')
#             if verbax not in axiom:
#                 axiom.append(verbax)

#     axiom = set(axiom)
#     axiom = list(axiom)
#     # print(axiom)
#     return types, axiom

# 品詞のチェック
def get_types(filename):
    tree = etree.parse(filename)
    root = tree.getroot()

    adjdic = {}
    adjlst = []
    # advdic = {}
    # advlst = []
    objlst = []
    numlst = []
    tverblst = []
    iverblst = []
    Flag = False

    for token in root.iter('token'):
        if (((token.attrib['pos'] == "JJ") or (token.attrib['pos'] == "JJR"))
           and (token.attrib['entity'] != "PRE")
           and (token.attrib['entity'] != "B-NORP")
           and (token.attrib['cat'] != "S[pss]\\NP")) \
           or (((token.attrib['pos'] == "RB")
                or (token.attrib['pos'] == "RBR"))
               and (((token.attrib['entity'])[:3] == 'POS')
                    or ((token.attrib['entity'])[:3] == 'NEG'))):
            if not token.attrib['base'] in adjlst \
               and '~' not in token.attrib['base']:
                adjlst.append(token.attrib['base'])
                if ((token.attrib['entity'])[:3] == 'POS') \
                   or ((token.attrib['entity'])[:3] == 'NEG'):
                    adjdic[token.attrib['base']] = token.attrib['entity']
        elif (token.attrib['pos'] == "NN") or (token.attrib['pos'] == "NNS"):
            if not token.attrib['base'] in objlst:
                objlst.append(token.attrib['base'])

        elif token.attrib['surf'] == "at~most":
            Flag = True

        elif token.attrib['pos'] == "CD" \
                and not token.attrib['surf'] == "half":
            if Flag:
                num = int(token.attrib['base']) + 1
                Flag = False
                if num not in numlst:
                    numlst.append(num)
            else:
                if '_' not in token.attrib['surf']:
                    num = int(token.attrib['base'])
                    if num not in numlst:
                        numlst.append(num)

        elif (token.attrib['pos'])[:2] == 'VB' and \
                not token.attrib['base'] == 'be':
            if '/NP' in token.attrib['cat'] or \
               '/PP' in token.attrib['cat'] or \
               'S[pss]' in token.attrib['cat']:
                if not token.attrib['base'] in tverblst:
                    tverblst.append(token.attrib['base'])
            else:
                if not token.attrib['base'] in iverblst:
                    iverblst.append(token.attrib['base'])

        else:
            pass
    return adjdic, adjlst, objlst, numlst, tverblst, iverblst


def get_formulas_from_xml(doc):
    formulas = [s.get('sem', None) for s in doc.xpath(
        './sentences/sentence/semantics[1]/span[1]')]
    return formulas


def get_antonyms(adjdic, antonyms):
    adjs = [k for k, v in adjdic.items()]
    for i in range(len(adjs) - 1):
        Flag = is_antonym(adjs[i], adjs[i + 1])
        if Flag:
            if adjdic[adjs[i]] == 'POS' and adjdic[adjs[i + 1]] == 'NEG':
                antonyms.append([adjs[i], adjs[i + 1]])
            else:
                antonyms.append([adjs[i + 1], adjs[i]])
    return antonyms


def prove_vampire(premises, conclusion, predicates, lst, axioms, mode, mode2=".pos"):
    adjdic, adjlst, objlst, numlst, tverblst, iverblst \
        = get_types(re.sub(".sem.xml", ".jigg.xml", ARGS.sem))
    antonyms = []
    types = []
    # if adjlst != []:
    #     antonyms = get_antonyms(adjdic, antonyms)
    # add axioms from comp
    # types, axioms2 = vampire_axioms(adjdic, antonyms, objlst, tverblst,
    #                                 iverblst, predicates, lst)
    # axioms += axioms2
    axioms = set(axioms)
    axioms = list(axioms)

    premises = axioms + premises
    premises.append(conclusion)
    # print(premises)
    fols = convert_to_tptp_proof(premises)
    # print(fols)

    type_f = []
    type_f_adj = []
    type_f_adj.extend(types)
    lems = []

    # ここも品詞ごとに公理を追加している？
    # for adj in adjlst:
    #     adj_type = 'tff(' + adj + '_type, type , ' + adj + \
    #                ' : $i * $int > $o).'
    #     type_f_adj.append(adj_type)

    # if len(numlst) >= 2:
    #     numlst.sort()
    #     for i in range(len(numlst) - 1):
    #         lem = '$less(' + str(numlst[i]) + ',' + str(numlst[i + 1]) + ')'
    #         f = lexpr(lem)
    #         lemma = convert_to_tptp(f)
    #         lems.append(lemma)
    # for pred in predicates:
    #     if pred[0] == 'much' or pred[0] == 'many' or pred[0] == 'few':
    #         adj_type = 'tff(' + pred[0] + '_type, type , ' + pred[0] + \
    #                    ' : $i * $int > $o).'
    #         type_f_adj.append(adj_type)
    #         if pred[0] == 'many':
    #             adj_type = 'tff(few_type, type , few : $i * $int > $o).'
    #             type_f_adj.append(adj_type)
    #         elif pred[0] == 'few':
    #             adj_type = 'tff(many_type, type , many : $i * $int > $o).'
    #             type_f_adj.append(adj_type)
    #         else:
    #             pass
    #         qu_lem = lexpr('all x y.(exists d.(' + pred[0] + '(x,d) & -'
    #                        + pred[0] + '(y,d)) -> all d.(' + pred[0] +
    #                        '(y,d) -> ' + pred[0] + '(x,d)))')
    #         qu_lem = convert_to_tptp(qu_lem)
    #         if qu_lem not in lems:
    #             lems.append(qu_lem)

    #     elif pred[0] == 'year' or pred[0] == 'num':
    #         type_f.append('tff(' + pred[0] + '_type, type , ' + pred[0] + ' : $int * $i > $o).')

    #     for naf in non_Sub:
    #         if pred[0] == naf:
    #             naf_type = 'tff(' + naf + '_type, type , ' + naf + \
    #                        ' : $o > $o).'
    #             type_f.append(naf_type)

    #     v_type = 'tff(acci_type, type , acci : $i * $o > $o).'
    #     type_f.append(v_type)

    #     for c in clause:
    #         if pred[0] == c:
    #             c_type = 'tff(' + c + '_type, type , ' + c + \
    #                      ' : $o * $o > $o).'
    #             type_f.append(c_type)

    #     for obj in objlst:
    #         if (pred[0] == obj) or (obj in pred[1][0]):
    #             obj_type = 'tff(' + obj + '_type, type , ' + obj + \
    #                        ' : $i > $o).'
    #             type_f.append(obj_type)

    #     type_f.append('tff(th_type, type , th : $i > $int).')
    #     type_f.append('tff(d0_type, type , d0 : $int).')

    #     if (len(pred[1]) == 2) and ('_np' in (pred[1])[1]):
    #         type_f.append('tff(np_type, type , np : $i * $int > $int).')

    type_f = set(type_f)
    type_f = list(type_f)
    type_f_adj = set(type_f_adj)
    type_f_adj = list(type_f_adj)

    for i in range(len(lems)):
        fols.insert(-1, 'tff(p{0},lemma,{1}).'.format(i, lems[i]))
    fols = type_f + type_f_adj + fols

    with open(ARGS.txt, 'r') as infile:
        sentences = infile.read().splitlines()
    problem_numstr = re.findall(r'(\d+)', ARGS.txt)
    problem_num = int(problem_numstr[0]) if problem_numstr != [] else 0

    arg = ARGS.sem.replace('en_parsed/', '')
    arg = arg.replace('.sem.xml', '')
    # with open("tptp/" + arg + ".tptp", "a", encoding="utf-8") as z:
    with open('./templates/temporal_types.tptp', 'r') as infile:
        type_info = infile.read()
    with open('./templates/temporal_adverbial_axioms.tptp', 'r') as infile:
        lines = infile.read().splitlines()
    time_axioms = []
    axioms = defaultdict(list)
    for line in lines:
        if ' %' in line:
            line_split = line.split(' %')
            axioms[line_split[1]].append(line)
    time_axioms += axioms["speech_time"]
    join_sentences = ''.join(sentences)
    events = []
    nort = False
    for f in fols:
        if '年' in f and '月' in f and '日' in f:
            time_axioms.append(axioms["normalized_time"][0])
        elif '年' in f and '月' in f:
            time_axioms.append(axioms["normalized_time"][1])
        elif '年' in f and '日' in f:
            time_axioms.append(axioms["normalized_time"][2])
        elif '月' in f and '日' in f:
            time_axioms.append(axioms["normalized_time"][3])
        elif '年' in f:
            time_axioms.append(axioms["normalized_time"][4])
        elif '月' in f:
            time_axioms.append(axioms["normalized_time"][5])
        elif '日' in f:
            time_axioms.append(axioms["normalized_time"][6])
        events += re.findall(r"('[^']+?')\(E\d+\)", f)
        if 'normalized_time' in f:
            nort = True
        if '最初' in f:
            time_axioms += axioms["first"]
        if '最後' in f:
            time_axioms += axioms["last"]
        if '設立' in f:
            time_axioms += axioms["establish"]
        if "以来" in join_sentences:
            if "ある" in f:
                time_axioms += axioms["irai_exist"]
            if "拡張" in f:
                time_axioms += axioms["irai_extend"]
            if "出す" in f:
                time_axioms += axioms["irai_emit"]
    time_axioms = list(set(time_axioms))
    events = list(set(events))
    if "現在" in sentences[-1]:
        time_axioms += axioms["now"]
    else:
        izen_c = join_sentences.count("以前")
        ikou_c = join_sentences.count("以後") + join_sentences.count("以降")
        if izen_c:
            time_axioms.append(axioms["temporal_order"][0])
            if izen_c > 1:
                time_axioms.append(axioms["temporal_order"][2])
        if ikou_c:
            time_axioms.append(axioms["temporal_order"][1])
            if ikou_c > 1:
                time_axioms.append(axioms["temporal_order"][3])

    if nort:
        event_axiom = axioms["event"][1]
    else:
        event_axiom = axioms["event"][0]
    for event in events:
        time_axioms.append(event_axiom.replace("'temp'", event))

    with open('./templates/temporal_relation_axioms.tptp', 'r') as infile:
        time_rel_axioms = infile.read()
    with open(arg + mode2 + ".tptp", "w", encoding="utf-8") as z:
        z.write('% type definition\n')
        z.write(type_info + '\n')
        ja_predicates = []
        for f in fols:
            ja_predicates += re.findall("'.+?'", f)
        ja_predicates = set(ja_predicates) - set(["'年'", "'月'", "'日'"])
        z.write("% japanese predicate type definition\n")
        for i, ja_predicate in enumerate(ja_predicates):
            f = ''.join(fols)
            if f"= {ja_predicate}" in f:
                continue
            elif f"{ja_predicate}(X" in f:
                type_str = f"tff(ja_predicate_{i+1}_type, type, {ja_predicate}: $i > $o).\n"
            else:
                type_str = f"tff(ja_predicate_{i+1}_type, type, {ja_predicate}: event > $o).\n"
            z.write(type_str)
        z.write('\n')
        z.write('% time relation axiom definition\n')
        z.write(time_rel_axioms + '\n')
        z.write('% time axiom definition\n')
        z.write('\n'.join(time_axioms) + '\n\n')
        z.write('% hypothesis and conjecture\n')
        for f in fols:
            z.write(f + "\n")
    with open(arg + mode2 + ".tptp", "r", encoding="utf-8") as infile:
        tptp_script = infile.read()
    ps = subprocess.Popen(('echo', tptp_script), stdout=subprocess.PIPE)
    try:
        if mode == 'casc_sat':
            timeout = '1'
        else:
            timeout = '7'
            if problem_num in [645, 647, 648, 649]:
                timeout = '300'
        output = subprocess.check_output(
            (vampire_dir + '/vampire', '-t', timeout, '--mode', mode),
            stdin=ps.stdout,
            stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        return False
    ps.wait()
    output_lines = [
        str(line).strip() for line in output.decode('utf-8').split('\n')]
    res = is_theorem_in_vampire(output_lines)
    return res


def is_theorem_in_vampire(output_lines):
    if output_lines:
        proof_message = '% Refutation found. Thanks to Tanya!'
        if (proof_message in output_lines):
            return True
        else:
            return False
    else:
        return False


def theorem_proving(prove_fun, premises, conclusion, predicates, lst, axioms,
                    mode, data):
    res = prove_fun(premises, conclusion, predicates, lst, axioms, mode)
    if res:
        prediction = 'yes'
    else:
        if data not in datasets:
            negated_conclusion = NegatedExpression(conclusion)
            res = prove_fun(premises, negated_conclusion, predicates, lst,
                            axioms, mode, ".neg")
            if res:
                prediction = 'no'
            else:
                prediction = 'unknown'
        else:
            prediction = 'unknown'
    return prediction


def get_predicate(formula):
    predlst = []
    preds = get_atomic_formulas(lexpr(formula))
    for pred in preds:
        if isinstance(pred, ApplicationExpression):
            predicate, args = pred.uncurry()
            pred_str = str(predicate)
            args_str = [str(arg) for arg in args]
            item = [pred_str, args_str]
            if item not in predlst:
                predlst.append(item)
    return predlst


def main(args=None):
    global ARGS
    global DOCS
    DESCRIPTION = textwrap.dedent("""
            The input file sem should contain the parsed sentences. '\
            'All CCG trees correspond to the premises, '\
            'except the last one, which is the hypothesis.
      """)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESCRIPTION)
    parser.add_argument("sem", help="XML input filename with semantics")

    parser.add_argument("txt", help="txt input filename")

    parser.add_argument("--prover", nargs='?', type=str, default="vampire",
                        choices=["vampire"],
                        help="Prover (default: vampire).")

    parser.add_argument("--abduction", nargs='?', type=str, default="nolex",
                        choices=["lex", "nolex"],
                        help="Abduction (default: nolex).")

    ARGS = parser.parse_args()

    if not os.path.exists(ARGS.sem):
        print('File does not exist: {0}'.format(ARGS.sem), file=sys.stderr)
        parser.print_help(file=sys.stderr)
        sys.exit(1)

    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.parse(ARGS.sem, parser)

    DOCS = root.findall('.//document')
    doc = DOCS[0]
    formulas = get_formulas_from_xml(doc)
    # print(formulas)
    # formulas = ['exists t.(True & exists e1.(_escape(e1) & (Nom(e1) = _taro) & before(time(e1),t) & exists e2.(before(time(e2),time(e1)) & _sleep(e2) & (Nom(e2) = _taro))))', \
    # 'exists t.(True & exists e1.(_escape(e1) & (Nom(e1) = _taro) & before(time(e1),t) & exists e2.(before(time(e1),time(e2)) & _sleep(e2) & (Nom(e2) = _taro))))']

    # add axioms from WordNet
    if ARGS.abduction == "lex":
        sentences = doc.xpath('//sentence')
        axioms = get_axioms(formulas, sentences)
    else:
        axioms = []

    lst = []
    predicates = []
    new_formulas = []
    for formula in formulas:
        if '--' in formula:
            formula = formula.replace('--', '')
        formula = rename_variable(lexpr(formula))  # rename_degree_variableだった
        new_formulas.append(str(formula))
    for formula in new_formulas:
        if ('all' in formula) and ('->' in formula) \
           and ('_th(' in formula):
            lst.append(formula)
        preds = get_predicate(formula)
        for pred in preds:
            if pred not in predicates:
                predicates.append(pred)

    p = re.compile(r'(\w+)/(\w+)_(\w+)_(\w+)')
    a = p.search(ARGS.sem)
    if a is not None:
        cache, data, num, other = a.groups()
    else:
        data = 'None'

    if ARGS.prover == "vampire":
        formulas = [lexpr(formula) for formula in new_formulas]
        premises = formulas[:-1]
        conclusion = formulas[-1]
        start = time.time()
        prediction = theorem_proving(prove_vampire, premises, conclusion,
                                     predicates, lst, axioms, 'casc', data)
        end = time.time() - start
        if prediction == 'unknown' and end >= 8:
            prediction = theorem_proving(prove_vampire, premises,
                                         conclusion, predicates,
                                         lst, axioms, 'casc_sat', data)
        # print('{0},{1:.4f}'.format(prediction, end))
        print(prediction)

# Test formulas
# f1 = lexpr('exists x. (boy(x) & tall(x))')
# f2 = lexpr('exists x. (boy(x))')
# f3 = lexpr('forall x. (boy(x) -> -tall(x))')
# f4 = lexpr('tall(john)')
# f5 = lexpr('-boy(john)')
# inf1 = [f1, f2]
# inf2 = [f2, f1]
# inf3 = [f3, f4, f5]
# formulas = ['exists x. (boy(x) & tall(x))', 'exists x. (boy(x))']


if __name__ == '__main__':
    main()
