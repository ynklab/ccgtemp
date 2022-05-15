from lxml import etree
import argparse
import re


def timenum(surf):
    time = 0
    year = re.search(r'(\d+)年', surf)
    month = re.search(r'(\d+)月', surf)
    date = re.search(r'(\d+)日', surf)
    gozen = re.search(r'午前', surf)
    gogo = re.search(r'午後', surf)
    zi = re.search(r'(\d+)時', surf)
    day = re.search(r'[月|火|水|木|金|土|日]曜', surf)
    if year:
        time += int(year.groups()[0]) * 1000000
    if month:
        time += int(month.groups()[0]) * 10000
    if date:
        time += int(date.groups()[0]) * 100
    if zi:
        time += int(zi.groups()[0])
        if gogo:
            time += 12
    elif gogo:
        time += 24
    elif gozen:
        time += 12
    if time < 100 and day:
        if day.group() == '月曜':
            time += 4100
        elif day.group() == '火曜':
            time += 4200
        elif day.group() == '水曜':
            time += 4300
        elif day.group() == '木曜':
            time += 4400
        elif day.group() == '金曜':
            time += 4500
        elif day.group() == '土曜':
            time += 4600
        elif day.group() == '日曜':
            time += 4700
    return time


parser = argparse.ArgumentParser()
parser.add_argument('TAGGED')
parser.add_argument('UNTAGGED')
parser.add_argument('PAT')
args = parser.parse_args()

pattern_file = args.PAT
with open(pattern_file, 'r') as infile:
    patterns = infile.read().splitlines()
patterns = [pattern for pattern in patterns if pattern != '']
patterns.append('\\d+日')

tagged = etree.parse(args.TAGGED)
untagged = etree.parse(args.UNTAGGED)
tagged_sentences = tagged.getroot().findall('*//sentence')
untagged_sentences = untagged.getroot().findall('*//sentence')

assert len(tagged_sentences) == len(untagged_sentences)

for untagged_sentence, tagged_sentence in zip(untagged_sentences, tagged_sentences):
    untagged_tokens = untagged_sentence.xpath('tokens[1]')[0]
    tagged_tokens = tagged_sentence.xpath('tokens[1]')[0]
    index = 0
    for utoken in untagged_tokens:
        tempflag = False
        for pattern in patterns:
            tempexs = re.search(pattern, utoken.attrib['surf'])
            if tempexs:
                tempflag = True
                break
        if tempflag:
            utoken.attrib['base'] = str(timenum(utoken.attrib['surf']))
            utoken.attrib['pos'] = '時間表現'
        else:
            for token in tagged_tokens:
                if token.attrib['surf'] == utoken.attrib['surf']:
                    token.attrib['start'] = utoken.attrib['start']
                    token.attrib['id'] = utoken.attrib['id']
                    untagged_tokens.remove(utoken)
                    untagged_tokens.insert(index, token)
                    break
            else:
                utoken.attrib['base'] = str(timenum(utoken.attrib['surf']))
                utoken.attrib['pos'] = '時間表現'
        index += 1


print(etree.tostring(untagged, encoding='utf-8', pretty_print=True).decode('utf-8'))
