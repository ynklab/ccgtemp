# -*- coding: utf-8 -*-

from nltk.sem.logic import *
from logic_parser import lexpr
from nltk2normal import rename_variable, remove_true, rename
import re

def convert_to_tptp_proof(formulas):
    if len(formulas) == 1:
        conjecture = formulas[0]
        tptp_script = ['tff(h,conjecture,{0}).'.format(conjecture)]
    else:
        premises, conjecture = formulas[:-1], formulas[-1]
        tptp_script = []
        num = 1
        for formula in premises:
            formula = convert_to_tptp(formula)
            tptp_script.append('tff(t{0},axiom,{1}).'.format(num,formula))
            num += 1
        conjecture = convert_to_tptp(conjecture)
        tptp_script.append('tff(h,conjecture,{0}).'.format(conjecture))
    return tptp_script

def convert_to_tptp(expression):
    # expression = rename_variable(expression)
    expression = remove_true(expression)
    expression = rename(expression)
    tptp_str = convert_tptp(expression)
    return tptp_str

def convert_tptp(expression):
    if isinstance(expression, ApplicationExpression):
        tptp_str = convert_tptp_application(expression)
    elif isinstance(expression, EqualityExpression):
        tptp_str = convert_tptp_equality(expression)
    elif isinstance(expression, AndExpression):
        tptp_str = convert_tptp_and(expression)
    elif isinstance(expression, OrExpression):
        tptp_str = convert_tptp_or(expression)
    elif isinstance(expression, ImpExpression):
        tptp_str = convert_tptp_imp(expression)
    elif isinstance(expression, IffExpression):
        tptp_str = convert_tptp_iff(expression)
    elif isinstance(expression, NegatedExpression):
        tptp_str = convert_tptp_not(expression)
    elif isinstance(expression, ExistsExpression):
        tptp_str = convert_tptp_exists(expression)
    elif isinstance(expression, AllExpression):
        tptp_str = convert_tptp_all(expression)
    elif isinstance(expression, LambdaExpression):
        tptp_str = convert_tptp_lambda(expression)
    elif isinstance(expression, IndividualVariableExpression):
        tptp_str = str(expression.variable).upper()
    elif isinstance(expression, EventVariableExpression):
        tptp_str = str(expression.variable).upper()
    elif isinstance(expression, FunctionVariableExpression):
        tptp_str = str(expression.variable).upper()
    elif isinstance(expression, ConstantExpression):
        tptp_str = str(expression.variable).lower()
        if tptp_str[0] == '_':
            if tptp_str[1:].isdecimal():
                tptp_str = tptp_str[1:]
            else:
                tptp_str = "'" + tptp_str[1:] + "'"
    else:
        tptp_str = str(expression)
    return tptp_str

def convert_tptp_application(expression):
    function, args = expression.uncurry()
    function_str = convert_tptp(function)
    args_str = ','.join(convert_tptp(arg) for arg in args)
    tptp_expr = function_str + Tokens.OPEN + args_str + Tokens.CLOSE
    return tptp_expr

def convert_tptp_equality(expression):
    first = convert_tptp(expression.first)
    second = convert_tptp(expression.second)
    tptp_str = Tokens.OPEN + first + ' = ' + second + Tokens.CLOSE
    return tptp_str

def convert_tptp_and(expression):
    first = convert_tptp(expression.first)
    second = convert_tptp(expression.second)
    tptp_str = Tokens.OPEN + first + ' & ' + second + Tokens.CLOSE
    return tptp_str

def convert_tptp_or(expression):
    first = convert_tptp(expression.first)
    second = convert_tptp(expression.second)
    tptp_str = Tokens.OPEN + first + ' | ' + second + Tokens.CLOSE
    return tptp_str

def convert_tptp_imp(expression):
    first = convert_tptp(expression.first)
    second = convert_tptp(expression.second)
    tptp_str = Tokens.OPEN + first + ' => ' + second + Tokens.CLOSE
    return tptp_str

def convert_tptp_iff(expression):
    first = convert_tptp(expression.first)
    second = convert_tptp(expression.second)
    tptp_str = Tokens.OPEN + first + ' <=> ' + second + Tokens.CLOSE
    return tptp_str

def convert_tptp_not(expression):
    term = convert_tptp(expression.term)
    tptp_str = Tokens.OPEN + "~" + term + Tokens.CLOSE
    return tptp_str

def convert_tptp_exists(expression):
    variable = convert_tptp(expression.variable).upper()
    term = convert_tptp(expression.term)
    if variable[0] == 'D':
        tptp_str = '?[' + variable + ':$int]: ' + Tokens.OPEN + term + Tokens.CLOSE
    elif variable[0] == 'E':
        tptp_str = '?[' + variable + ':event]: ' + Tokens.OPEN + term + Tokens.CLOSE
    elif variable[0] == 'X' and is_interval(term, variable):
        tptp_str = '?[' + variable + ':interval]: ' + Tokens.OPEN + term + Tokens.CLOSE
    else:
        tptp_str = '?[' + variable + ']: ' + Tokens.OPEN + term + Tokens.CLOSE
    return tptp_str

def is_interval(term, variable):
    ja_predicates = re.findall(r"'(.+?)'\(" + re.escape(variable) + r"\)", term)
    # ja_predicates = [predicate for predicate in predicates if not re.findall(r'^[a-zA-Z0-9\-\_]+', predicate)]
    if len(set(['年', '月', '日']) - set(ja_predicates)) != 3 or ja_predicates == []:
        return True
    else:
        return False

def convert_tptp_all(expression):
    variable = convert_tptp(expression.variable).upper()
    term = convert_tptp(expression.term)
    if variable[0] == 'D':
        tptp_str = '![' + variable + ':$int]: ' + Tokens.OPEN + term + Tokens.CLOSE
    elif variable[0] == 'E':
        tptp_str = '![' + variable + ':event]: ' + Tokens.OPEN + term + Tokens.CLOSE
    elif variable[0] == 'X':
        tptp_str = '![' + variable + ':interval]: ' + Tokens.OPEN + term + Tokens.CLOSE
    else:
        tptp_str = '![' + variable + ']: ' + Tokens.OPEN + term + Tokens.CLOSE
    return tptp_str

def convert_tptp_lambda(expression):
    variable = convert_tptp(expression.variable).upper()
    term = convert_tptp(expression.term)
    tptp_str = '?[' + variable + ']: ' + Tokens.OPEN + term + Tokens.CLOSE
    return tptp_str
