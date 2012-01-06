import types
from interface import *
import copy

def solve(trace, var):
	equ = build_equ(trace, var)
	return execute(equ)

def solveBoth(trace, var):
	equ = build_equ(trace, var)
	return (execute(equ[2]), execute(equ[3]))

def build_equ(trace, var):
	equ = var
	need = [var]
	neededNext = []
	for inst in reversed(trace):
		for v in need[:]:
			if v in inst.effects:
				equ = replace(v, inst.effects[v], equ)
				need.remove(v)
				neededNext += needed(inst.effects[v])
		need = Sexpression(set(neededNext + need))
		if len(need) == 0:
			return equ
	return equ

def needed(eq):
	""" Iterates over an equation and returns a list of any missing variables 
	"""
	need = []
	if type(eq) is str:
		need.append(eq) 
	elif type(eq) is Sexpression:
		for i in range(len(eq)):
			need += needed(eq[i])
	return need


def replace(var, with_equ, in_equ):
	out = in_equ
	if out == var:
		out = copy.deepcopy(with_equ) # Make sure we get a copy, otherwise solved equations might escape.
	elif type(out) is Sexpression:
		for i in range(len(out)):
			out[i] = replace(var, with_equ, out[i])
	return out 

def execute(eq):
	if type(eq) is Sexpression:
		if type(eq[0]) is not types.FunctionType:
			raise Exception("Invalid s-expression doesn't start with function\n%s" % eq)
		for i in range(1, len(eq)):
			if type(eq[i]) is Sexpression:
				eq[i] = execute(eq[i])
		for arg in eq[1:]:
			if type(arg) is not int:
				return eq
		return eq[0](*eq[1:])
	return eq
