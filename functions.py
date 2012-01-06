def infix(fmt):
	def decorator(fn):
		def pp(t):
			return fmt % t
		fn.pp = pp
		return fn
	return decorator

def conditional(fn):
	fn.conditional = True
	return fn

@infix("%s + %s")
def add(a, b):
	return a + b

@infix("%s - %s")
def sub(a, b):
	return a - b

@infix("%s & %s")
def andl(a, b):
	return a & b


@infix("%s ^ %s")
def xorl(a, b):
	return a ^ b

@infix("%s | %s")
def orl(a, b):
	return a | b

def bit(bit, val):
	mask = ~(1 << bit)
	return int(not (val ^ mask)) 

@infix("%s > %s")
def gt(a, b):
	return int(a > b)

@infix("%s < %s")
def lt(a, b):
	return int(a < b)

@infix("%s == %s")
def eq(a, b):
	return int(a == b)

@infix("%s * %s")
def mul(a, b):
	return a * b

@infix("%s %% %s")
def mod(val, d):
	return val % d

class Memory8(object):
	def __init__(self, addr):
		self.addr = addr

	def __repr__(self):
		if type(self.addr) is int:
			return "mem8[0x%04x]" % self.addr
		return "mem8[%s]" % self.addr

class Memory16(object):
	def __init__(self, addr):
		self.addr = addr

	def __repr__(self):
		if type(self.addr) is int:
			return "mem16[0x%04x]" % self.addr
		return "mem16[%s]" % self.addr

	def infix(self):
		return self.__repr__()

def rotleft(shift, size, value):
	value = value << shift
	value = (value & ((1 << size) - 1)) | value >> size
	return value

def rotright(shift, size, value):
	overflow = value & ((1 << shift) -1)
	value = (value >> shift) | overflow << (size - shift)
	return value

def shiftleft(shift, value):
	return value << shift

def shiftright(shift, value):
	return value >> shift

@conditional
@infix("if (%s): %s else %s")
def if_(cond, expr1, expr2):
	if cond:
		return expr1
	else:
		return expr2
if_.func_name = "if"
