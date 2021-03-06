#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import codecs
import logging
from lxml import etree
import os
import sys
import textwrap

from visualization_tools import convert_root_to_mathml
from visualization_vertical_tools import convert_vertical_to_mathml
from visualization_latex import convert_doc_to_latex

def main(args = None):
    DESCRIPTION=textwrap.dedent("""\
            Prints graphically in HTML the CCG tree. If <semantics> content
            is also present in the XML file, then logical formulas appear
            below the syntactic categories to show the semantic composition.
            The input file with the CCG tree should follow Jigg's format:
            https://github.com/mynlp/jigg
      """)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESCRIPTION)
    parser.add_argument("trees_xml")

    parser.add_argument("--format", nargs='?', type=str, default="plain",
        choices=["plain", "vertical", "latex"],
        help="Graphical tree output (default: plain CCG tree).")

    args = parser.parse_args()

    if not os.path.exists(args.trees_xml):
        print('File does not exist: {0}'.format(args.trees_xml))
        sys.exit(1)

    logging.basicConfig(level=logging.WARNING)

    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.parse(args.trees_xml, parser)

    if args.format == "plain":
        html_str = convert_root_to_mathml(root)
        print(html_str)

    if args.format == "vertical":
        html_str = convert_vertical_to_mathml(root)
        print(html_str)

    if args.format == "latex":
        latex_str = convert_doc_to_latex(root)
        print(latex_str)

if __name__ == '__main__':
    main()
