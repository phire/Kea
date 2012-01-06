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
		self.decoded = {}
		
	def attachMemory(self, memory):
		self.mem = memory
		for i in xrange(len(memory)):
			self.decoded[i] = [Text("db ", blue), Text("0x%02x" % ord(self.mem[i]), green)]

	def startTrace(self, address):
		trace = [StartTrace(address)]
		pc = solver.solve(trace, self.pc)
		while type(pc) is int and pc < 0x4000:
			stream = Stream(self.mem, pc)
			inst = self.proc.decode(None, stream)
			trace.append(inst)
			self.decoded[pc] = [Text(inst.asm, blue)]
			count = stream.count
			while count > 1:
				count -= 1
				try:
					del self.decoded[pc + count]
				except KeyError:
					pass
			pc = solver.solve(trace, self.pc)
		self.notifyObservers()
	
	def addObserver(self, observer):
		self.observers.append(observer)

	def notifyObservers(self):
		for observer in self.observers:
			observer.notify(self)

	def getText(self, start, length):
		text = []
		lines = sorted(self.decoded.keys())
		for i in range(start, start + length):
			try:
				text.append([Text("ROM0:%04x" % lines[i], gray), Tab(100)] + self.decoded[lines[i]])
			except KeyError:
				break
		return text

	def getTextSize(self):
		return len(self.decoded)

	def makeCode(self, line):
		lines = sorted(self.decoded.keys())
		self.startTrace(lines[line])

if __name__ == "__main__":
	core = Core(gz80())
	core.attachMemory(open("page00").read())
	core.startTrace(0x100)
