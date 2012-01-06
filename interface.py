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

	def contains(self, reg):
		for x in self[1:]:
			if type(x) is Sexpression:
				if x.contains(reg):
					return True
			elif x == reg:
				return True
		return False

	def isConditional(self):
		return hasattr(self[0], "conditional")

class Instruction(object):
	def __setattr__(self, *args):
		raise TypeError("can't modify immutable instance")
	__delattr__ = __setattr__
	def __init__(self, asm, effects):
		super(Instruction, self).__setattr__('asm', asm)	#self.asm = asm
		for e in effects.keys():
			if type(effects[e]) is list:
				effects[e] = Sexpression(effects[e])
		super(Instruction, self).__setattr__('effects', effects) #self.effects = effects

	def __repr__(self):
		return self.asm

	def prettyPrint(self):
		return self.asm

	def stores(self, reg):
		""" If this instruciton stores reg into another register or a 
			memory address, this will return that memory address/register.
			Otherwise, returns None.
		"""
		for e in self.effects.keys():
			if type(self.effects[e]) is Sexpression:
				if self.effects[e].contains(reg):
					if e is not reg:
						return e
		return None

class Address(object):
	def __init__(self, addr):
		pass

#class RealtiveAddress(Address):
