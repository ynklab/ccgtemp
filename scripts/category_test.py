#!/usr/bin/python3
# -*- coding: utf-8 -*-

import unittest

from category import Category

class CategoryTestCase(unittest.TestCase):
    def test_category_matches(self):
        cat1 =  Category('N')
        cat2 =  Category('N')
        self.assertTrue(cat1.match(cat2))

    def test_category_no_matches(self):
        cat1 =  Category('N')
        cat2 =  Category('X')
        self.assertFalse(cat1.match(cat2))

    def test_category_feat_equal_matches(self):
        cat1 =  Category('N[dcl=true]')
        cat2 =  Category('N[dcl=true]')
        self.assertTrue(cat1.match(cat2))

    def test_category_feat_diff_no_matches(self):
        cat1 =  Category('N[dcl=true]')
        cat2 =  Category('N[dcl=false]')
        self.assertFalse(cat1.match(cat2))

    def test_category_feat_disjoint_no_matches(self):
        cat1 =  Category('N[dcl=true]')
        cat2 =  Category('N[pss=true]')
        self.assertFalse(cat1.match(cat2))

    def test_category_nofeat_feat_matches(self):
        cat1 =  Category('N')
        cat2 =  Category('N[dcl=true]')
        self.assertTrue(cat1.match(cat2))

    def test_category_nofeat_feat_no_matches(self):
        cat1 =  Category('N[dcl=true]')
        cat2 =  Category('N')
        self.assertFalse(cat1.match(cat2))

    def test_multiple_feat_strip(self):
        cat1 =  Category('N[dcl=true]/N[f=a]')
        self.assertEqual(str(cat1.types), 'N/N')

    def test_left_arg_bar(self):
        cat1 =  Category('NP/NP')
        cat2 =  Category('NP/NP')
        self.assertTrue(cat1.match(cat2))

    def test_left_arg_bar_not_match(self):
        cat1 =  Category('NP/NP')
        cat2 =  Category('NP')
        self.assertFalse(cat1.match(cat2))

    def test_left_arg_bar_not_match_right_arg(self):
        cat1 =  Category('NP/NP')
        cat2 =  Category('NP\\NP')
        self.assertFalse(cat1.match(cat2))

    def test_vertical_bar_right_bar_match(self):
        cat1 =  Category('NP|NP')
        cat2 =  Category('NP/NP')
        self.assertTrue(cat1.match(cat2))

    def test_vertical_bar_left_bar_match(self):
        cat1 =  Category('NP|NP')
        cat2 =  Category('NP\\NP')
        self.assertTrue(cat1.match(cat2))

    def test_hyphen_not_match(self):
        cat1 =  Category('NP-NP')
        cat2 =  Category('NP/NP')
        self.assertFalse(cat1.match(cat2))

    def test_substring_not_match(self):
        cat1 =  Category('NP/NP')
        cat2 =  Category('NP/NPZ')
        self.assertFalse(cat1.match(cat2))

    def test_vertical_bar_complex_match(self):
        cat1 =  Category('NP|NP|NP')
        cat2 =  Category('NP/NP\\NP')
        self.assertTrue(cat1.match(cat2))

    def test_vertical_bar_parenthesis_match(self):
        cat1 =  Category('(NP/NP)|NP')
        cat2 =  Category('(NP/NP)\\NP')
        self.assertTrue(cat1.match(cat2))


if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(CategoryTestCase)
    suites = unittest.TestSuite([suite1])
    unittest.TextTestRunner(verbosity=2).run(suites)
