from gz80 import gz80
from interface import ProgramCounter
from bus import Stream
import solver
from text import *

class StartTrace(object):
	def __init__(self, address):
		self.effects = {"pc": address}

	def __repr__(self):
		return "Start" + str(self.effects)

class Core(object):
	def __init__(self, processor):
		self.proc = processor
		self.regs = processor.getDescription()
		for reg in self.regs: # Find the program counter
			if type(self.regs[reg]) is ProgramCounter:
				self.pc = reg
		self.observers = []
		self.decoded = {}
		self.stack = []
		
	def attachMemory(self, memory):
		self.mem = memory
		for i in xrange(len(memory)):
			self.decoded[i] = [Text("db ", blue), Text("0x%02x" % ord(self.mem[i]), green)]
		self.makeCode(0x100)

	def startTrace(self, address):
		print "Start Trace " + hex(address)
		trace = [StartTrace(address)]
		pc = solver.solve(trace, self.pc)
		while type(pc) is int and pc < 0x4000:
			if str(self.decoded[pc][0]) != "db ":
				self.notifyObservers()
				return
			stream = Stream(self.mem, pc)
			inst = self.proc.decode(None, stream)
			if inst is None:
				print "Invalid Instruction"
				return
			trace.append(inst)
			self.decoded[pc] = [Text(inst.asm, blue)]
			count = stream.count
			while count > 1:
				count -= 1
				try:
					del self.decoded[pc + count]
				except KeyError:
					pass
			if inst.stores(self.pc): # If the program counter gets stored somewhere (aka, a function call)
				# Push the computed pc value on the stack to be explored later
				self.stack.append(solver.solve(trace, inst.stores(self.pc)))
			try: # if there is a conditional jump, then we follow both paths.
				if inst.effects[self.pc].isConditional():
					a, b = solver.solveBoth(trace, self.pc);
					self.stack.append(a)
					self.stack.append(b)
					self.notifyObservers()
					return
			except:
				pass
			pc = solver.solve(trace, self.pc)
		self.notifyObservers()
		try:
			print "pc = " + pc.infix()
		except:
			print "pc = 0x%x" % (pc)
	
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
		self.stack.append(lines[line])
		while(len(self.stack)):
			self.startTrace(self.stack.pop())

if __name__ == "__main__":
	core = Core(gz80())
	core.attachMemory(open("page00").read())
	core.startTrace(0x88)
