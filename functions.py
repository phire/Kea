def add(a, b):
	return a + b

def sub(a, b):
	return a - b

def andl(a, b):
	return a & b

def xorl(a, b):
	return a ^ b

def orl(a, b):
	return a | b

def bit(bit, val):
	mask = ~(1 << bit)
	return not (val ^ mask) 

def gt(a, b):
	return a > b

def lt(a, b):
	return a < b

def eq(a, b):
	return a == b

def mul(a, b):
	return a * b

def mod(val, d):
	return val % d

class Memory8(object):
	def __init__(self, addr):
		self.addr = addr

	def __repr__(self):
		if type(self.addr) is int:
			return "(0x%04x)" % self.addr
		return "(%s)" % self.addr

class Memory16(object):
	def __init__(self, addr):
		self.addr = addr

	def __repr__(self):
		if type(self.addr) is int:
			return "(0x%04x)" % self.addr
		return "(%s)" % self.addr

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

def if_(cond, expr1, expr2):
	if cond:
		return expr1
	else:
		return expr2
