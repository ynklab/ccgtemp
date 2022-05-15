# -*- coding: utf-8 -*-

from lxml import etree

def get_node_at_path(tree, path):
    """
    `tree` is a lxml etree.
    `path` is either a list of indices (integer) or
    a single integer.
    It returns the lxml node of the tree at path `path`.
    """
    assert isinstance(path, list) or isinstance(path, int)
    if isinstance(path, int):
        path = [path]
    node = tree
    for d in path:
        try:
            node = node[d]
        except IndexError:
            raise(IndexError, 'Attempted to index subtree {0} with path {1}'\
                  .format(tree.get('id'), path))
    return node
