from gz80 import gz80
from interface import ProgramCounter
from bus import Stream

class Core(object):
	def __init__(self, processor):
		self.proc = processor
		self.regs = processor.getDescription()
		for reg in self.regs: # Find the program counter
			if type(self.regs[reg]) is ProgramCounter:
				self.pc = reg
		
		
	def attachMemory(self, memory):
		self.mem = memory

	def disassemble(self, address):
		inst = self.proc.decode(None, Stream(self.mem, address))
		return inst

core = Core(gz80())
core.attachMemory(open("page00").read())

