from __future__ import print_function
import argparse
import logging
from lxml import etree
from multiprocessing import Lock
import os
import sys
import textwrap
from ccg2lambda_tools import assign_semantics_to_ccg
from semantic_index import SemanticIndex

SEMANTIC_INDEX = None
ARGS = None
SENTENCES = None
kMaxTasksPerChild = None
lock = Lock()


def main(args=None):
    global SEMANTIC_INDEX
    global ARGS
    global SENTENCES
    DESCRIPTION = textwrap.dedent("""\
            categories_template.yaml should contain the semantic templates
              in YAML format.
            parsed_sentence.xml contains the CCG-parsed sentences.
            If --arbi-types is specified, then the arbitrary specification of
              types is enabled, thus using the argument as the field of the semantic
              template that is used. E.g, by specifying "--arbi-types coq_type"
              and a semantic template:
            - semantics: \\P x.P(x)
              category: NP
              coq_type: Animal
            The type "Animal" will be used for this expression. Otherwise,
            types of the sem/logic module of NLTK are used.
      """)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESCRIPTION)
    parser.add_argument("ccg")
    parser.add_argument("templates")
    parser.add_argument("sem")
    parser.add_argument("--arbi-types", action="store_true", default=False)
    parser.add_argument("--gold_trees", action="store_true", default=True)
    parser.add_argument("--nbest", nargs='?', type=int, default="0")
    parser.add_argument("--ncores", nargs='?', type=int, default="3",
                        help="Number of cores for multiprocessing.")
    ARGS = parser.parse_args()

    if not os.path.exists(ARGS.templates):
        print('File does not exist: {0}'.format(ARGS.templates))
        sys.exit(1)

    if not os.path.exists(ARGS.ccg):
        print('File does not exist: {0}'.format(ARGS.ccg))
        sys.exit(1)

    logging.basicConfig(level=logging.WARNING)

    SEMANTIC_INDEX = SemanticIndex(ARGS.templates)

    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.parse(ARGS.ccg, parser)

    SENTENCES = root.findall('.//sentence')

    assign_semantics_to_ccg(SENTENCES[0], SEMANTIC_INDEX, 1)


if __name__ == '__main__':
    main()
