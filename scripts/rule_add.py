import sys

ifile = sys.argv[1]
with open(ifile, 'r') as infile:
    lines = infile.read().splitlines()

lines = [line.replace('rule="&lt;un&gt;"', 'rule="&lt;time&gt;"') for line in lines]

with open(ifile, 'w') as outfile:
    for line in lines:
        outfile.write(f'{line}\n')
