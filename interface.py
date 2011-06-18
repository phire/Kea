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

class Instruction(object):
	def __init__(self, asm, effects):
		self.asm = asm
		self.effects = effects

	def __repr__(self):
		return self.asm
