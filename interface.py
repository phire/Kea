class Processor(object):
	""" All Processor modules implement this class."""

	def getDescription(self):
		""" Returns the register layout of the cpu """
		return None

	def decodeInstruction(self, state, stream):
		""" Decodes a single instruction.
		    State contains any registers that might effect the decoding
		    for example, thumb mode on arm.
		    Stream is a source of bytes for the processor module to decode. 
		    Returns an Instruction object.
		"""
		return None

class Register(object):
	def __init__(self, size):
		self.size = size

class ProgramCounter(Register):
	pass

class SubRegister(Register):
	def __init__(self, parent, size, offset):
		self.parent = parent
		self.size = size
		self.offset = offset

class Sexpression(list):
	def __init__(self, l):
		for i, x in enumerate(l):
			if type(x) is list:
				l[i] = Sexpression(x)
		super(Sexpression, self).__init__(l)

	def __str__(self):
		string = "(" + self[0].func_name
		for x in self[1:]:
			string += " "
			string += str(x)
		return string + ")"

	def infix(self):
		t = tuple([x.infix() if type(x) is Sexpression else x for x in self[1:]])
		return self[0].pp(t)

class Instruction(object):
	def __init__(self, asm, effects):
		self.asm = asm
		for e in effects.keys():
			if type(effects[e]) is list:
				effects[e] = Sexpression(effects[e])
		self.effects = effects

	def __repr__(self):
		return self.asm

	def prettyPrint(self):
		return self.asm

class Address(object):
	def __init__(self, addr):
		pass

#class RealtiveAddress(Address):
