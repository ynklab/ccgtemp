from collections import defaultdict
import os
import sys


def make_jsem():
    with open('data/jsem/jsem_temporal_order.csv', 'r') as infile:
        lines = infile.read().splitlines()[1:]

    lines = [line.split(',') for line in lines]
    paths = []
    os.makedirs('./jsem_plain', exist_ok=True)
    os.makedirs('./jsem_plain/jsem_temporal_order', exist_ok=True)

    for line in lines:
        premises = line[1].split('。')
        with open(f'jsem_plain/jsem_temporal_order/jsem_{line[0]}_temporal_reference.txt', 'w') as out:
            out.write("。\n".join(premises) + f'{line[2]}')
        with open(f'jsem_plain/jsem_temporal_order/jsem_{line[0]}_temporal_reference.answer', 'w') as out:
            if line[3] == "Entailment":
                out.write('yes')
            elif line[3] == "Contradiction":
                out.write('no')
            else:
                out.write('unknown')

        paths.append(f'jsem_plain/jsem_temporal_order/jsem_{line[0]}_temporal_reference.txt')

    paths = sorted(paths)
    with open('jsem_plain/jsem_temporal_order_problems_list', 'w') as out:
        out.write('\n'.join(paths))
    with open('jsem_plain/jsem_problems_list', 'w') as out:
        out.write('\n'.join(paths))


def make_plmute():
    with open('data/plmute/cs1_test_ja.csv', 'r') as infile:
        lines = infile.read().splitlines()[1:]

    lines = [line.split(',') for line in lines]
    os.makedirs('./plmute_plain', exist_ok=True)

    ty_count = defaultdict(int)
    paths = []
    paths_cat = defaultdict(list)
    for line in lines:
        ty = line[5]
        if ty_count[ty] == 0:
            os.makedirs(f'./plmute_plain/plmute_{ty.lower()}', exist_ok=True)
        with open(f'plmute_plain/plmute_{ty.lower()}/plmute_{ty.lower()}_{ty_count[ty]:03}.txt', 'w') as out:
            out.write(f'{line[1]}\n{line[2]}')
        with open(f'plmute_plain/plmute_{ty.lower()}/plmute_{ty.lower()}_{ty_count[ty]:03}.answer', 'w') as out:
            if line[3] == "Entailment":
                out.write('yes')
            elif line[3] == "Contradiction":
                out.write('no')
            else:
                out.write('unknown')
        paths.append(f'plmute_plain/plmute_{ty.lower()}/plmute_{ty.lower()}_{ty_count[ty]:03}.txt')
        paths_cat[ty].append(f'plmute_plain/plmute_{ty.lower()}/plmute_{ty.lower()}_{ty_count[ty]:03}.txt')
        ty_count[ty] += 1

    paths = sorted(paths)
    with open('plmute_plain/plmute_problems_list', 'w') as out:
        out.write('\n'.join(paths))
    for key in paths_cat:
        with open(f'plmute_plain/plmute_{key.lower()}_problems_list', 'w') as out:
            out.write('\n'.join(paths_cat[key]))


if __name__ == "__main__":
    args = sys.argv
    if len(args) == 2:
        if args[1] == "jsem":
            make_jsem()
        elif args[1] == "plmute":
            make_plmute()
        else:
            print("usage: python3 make_problems.py {jsem/plmute}")
    else:
        print("usage: python3 make_problems.py {jsem/plmute}")
