from gz80 import gz80
from interface import ProgramCounter
from bus import Stream
import solver
from text import *

class StartTrace(object):
	def __init__(self, address):
		self.effects = {"pc": address, "a": 0x11}

class Core(object):
	def __init__(self, processor):
		self.proc = processor
		self.regs = processor.getDescription()
		for reg in self.regs: # Find the program counter
			if type(self.regs[reg]) is ProgramCounter:
				self.pc = reg
		self.observers = []
		self.text = [[Text("ROM0:0150", gray), Tab(100), Text("cp ", blue), Text("a", orange), Text(", ", blue), Text("0x11", green)],[Text("ROM0:0152", gray), Tab(100), Text("jr ", blue), Text("z", orange), Text(", ", blue), Text("0x157", green)]]

		
	def attachMemory(self, memory):
		self.mem = memory

	def startTrace(self, address):
		trace = [StartTrace(address)]
		pc = solver.solve(trace, self.pc)
		while type(pc) is int:
			inst = self.proc.decode(None, Stream(self.mem, pc))
			trace.append(inst)
			print inst
			pc = solver.solve(trace, self.pc)
		print trace
		print pc
	
	def addObserver(self, observer):
		self.observers.append(observer)

	def notifyObservers(self):
		for observer in self.observers:
			observer.notify(self)

	def getText(self, start, length):
		return self.text

if __name__ == "__main__":
	core = Core(gz80())
	core.attachMemory(open("page00").read())
	core.startTrace(0x100)
