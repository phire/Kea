import types

def solve(trace, var):
	equ = build_equ(trace, var)
#	print equ
	return execute(equ)

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
		need = list(set(neededNext + need))
		if len(need) == 0:
			return equ
	return equ

def needed(eq):
	""" Iterates over an equation and returns a list of any missing variables 
	"""
	need = []
	if type(eq) is str:
		need.append(eq) 
	elif type(eq) is list:
		for i in range(len(eq)):
			need += needed(eq[i])
	return need


def replace(var, with_equ, in_equ):
	out = in_equ
	if type(out) is str and out == var:
		out = with_equ
	elif type(out) is list:
		for i in range(len(out)):
			out[i] = replace(var, with_equ, out[i])
	return out 

def execute(eq):
	if type(eq) is list:
		if type(eq[0]) is not types.FunctionType:
			raise Exception("Invalid s-expression doesn't start with function\n%s" % eq)
		for i in range(1, len(eq)):
			if type(eq[i]) is list:
				eq[i] = execute(eq[i])
		for arg in eq[1:]:
			if type(arg) is not int:
				return eq
		return eq[0](*eq[1:])
	return eq
