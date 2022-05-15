from lxml import etree
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('TAGGED')
parser.add_argument('UNTAGGED')
args = parser.parse_args()

tagged = etree.parse(args.TAGGED)
untagged = etree.parse(args.UNTAGGED)
tagged_sentences = tagged.getroot().findall('*//sentence')
untagged_sentences = untagged.getroot().findall('*//sentence')
assert len(tagged_sentences) == len(untagged_sentences)

for untagged_sentence, tagged_sentence in zip(untagged_sentences, tagged_sentences):
    untagged_tokens = untagged_sentence.xpath('tokens[1]')[0]
    tagged_tokens = tagged_sentence.xpath('tokens[1]')[0]
    for token in untagged_tokens:
        untagged_tokens.remove(token)
    untagged_tokens.extend(tagged_tokens.xpath('token'))

print(etree.tostring(untagged, encoding='utf-8', pretty_print=True).decode('utf-8'))
