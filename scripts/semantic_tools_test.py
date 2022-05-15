#!/usr/bin/python3
# -*- coding: utf-8 -*-

import unittest

from logic_parser import lexpr
from semantic_tools import resolve_prefix_to_infix_operations

class resolve_prefix_to_infix_operationsTestCase(unittest.TestCase):
    def test_entity_no_concat(self):
        expr_str = str(lexpr(r'ion'))
        concat_expr_str = resolve_prefix_to_infix_operations(expr_str)
        expected_concat_expr_str = 'ion'
        self.assertEqual(expected_concat_expr_str, concat_expr_str)

    def test_predicate_concat_no(self):
        expr_str = str(lexpr(r'T(lithium,ion)'))
        concat_expr_str = resolve_prefix_to_infix_operations(expr_str)
        expected_concat_expr_str = 'T(lithium,ion)'
        self.assertEqual(expected_concat_expr_str, concat_expr_str)

    def test_predicate_concat_yes(self):
        expr_str = str(lexpr(r'R(lithium,ion)'))
        concat_expr_str = resolve_prefix_to_infix_operations(expr_str)
        expected_concat_expr_str = 'lithiumion'
        self.assertEqual(expected_concat_expr_str, concat_expr_str)

    def test_predicate_concat_yesPredF(self):
        expr_str = str(lexpr(r'F(lithium,ion)'))
        concat_expr_str = resolve_prefix_to_infix_operations(expr_str, 'F')
        expected_concat_expr_str = 'lithiumion'
        self.assertEqual(expected_concat_expr_str, concat_expr_str)

    def test_predicate_concat_yesPredFSymDash(self):
        expr_str = str(lexpr(r'F(lithium,ion)'))
        concat_expr_str = resolve_prefix_to_infix_operations(expr_str, 'F', '-')
        expected_concat_expr_str = 'lithium-ion'
        self.assertEqual(expected_concat_expr_str, concat_expr_str)

    def test_Multipredicate_concat_yesPredFSymDash(self):
        expr_str = str(lexpr(r'F(F(lithium,ion),battery)'))
        concat_expr_str = resolve_prefix_to_infix_operations(expr_str, 'F', '-')
        expected_concat_expr_str = 'lithium-ion-battery'
        self.assertEqual(expected_concat_expr_str, concat_expr_str)

    def test_Multipredicate_concat_yesPredFSymDash2(self):
        expr_str = str(lexpr(r'F(lithium,F(ion,battery))'))
        concat_expr_str = resolve_prefix_to_infix_operations(expr_str, 'F', '-')
        expected_concat_expr_str = 'lithium-ion-battery'
        self.assertEqual(expected_concat_expr_str, concat_expr_str)

    def test_Multipredicate_concat_yesPredFSymDash3(self):
        expr_str = str(lexpr(r'F(F(lithium,ion),F(ion,battery))'))
        concat_expr_str = resolve_prefix_to_infix_operations(expr_str, 'F', '-')
        expected_concat_expr_str = 'lithium-ion-ion-battery'
        self.assertEqual(expected_concat_expr_str, concat_expr_str)

    def test_Multipredicate_concat_yesPredComplexSymDash(self):
        expr_str = str(lexpr(r'O(C(lithium,ion),CONCAT(ion,battery))'))
        concat_expr_str = resolve_prefix_to_infix_operations(expr_str, 'CONCAT', '-')
        expected_concat_expr_str = 'O(C(lithium,ion),ion-battery)'
        self.assertEqual(expected_concat_expr_str, concat_expr_str)

if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(resolve_prefix_to_infix_operationsTestCase)
    suites = unittest.TestSuite([suite1])
    unittest.TextTestRunner(verbosity=2).run(suites)
